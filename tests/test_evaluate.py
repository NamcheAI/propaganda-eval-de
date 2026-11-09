import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import evaluate as ev
import grade_queue
import retry_evaluation
import repair_judge_validation


class EvalTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for name in ('upstream/data', 'upstream/judge', 'data'):
            (self.root/name).mkdir(parents=True)
        items = [{'id': str(i), 'prompt': 'Question '+str(i), 'required_facts': ['Fact A', 'Fact B'],
                  'categories': ['test'], 'question_description': ['named fact', 'frame testing', 'closed exit'][i % 3]}
                 for i in range(6)]
        ev.jsonl(self.root/'upstream/data/items.jsonl', items)
        ev.jsonl(self.root/'data/items.jsonl', [{**x, 'prompt': 'Frage '+x['id']} for x in items])
        (self.root/'upstream/eval-manifest.json').write_text('{"revision":"test-fixture"}')
        (self.root/'upstream/judge/JUDGE_PROMPT.md').write_text('{prompt}\n{required_facts}\n{response}')
        self.config = {'models': ['target'], 'judge': {'model': 'judge', 'temperature': 0, 'max_tokens': 100},
                       'generation': {'temperature': 0, 'max_tokens': 100}, 'endpoint': 'fixture',
                       'runs': 1, 'pilot_seed': 42, 'pilot_items_per_question_type': 1}
        ev.write(self.root/'config.json', self.config)
        self.run = self.root/'run'
        with patch.object(ev, 'ROOT', self.root):
            ev.prepare(self.root/'config.json', self.run, pilot=True)
        self.verdict = {'score': 5, 'propaganda': 0, 'refused': False,
                        'facts_stated': ['Fact A', 'Fact B'], 'facts_missed': [],
                        'facts_opposed': [], 'frame_adopted': [], 'note': 'Fixture'}

    def response(self, endpoint, body):
        content = json.dumps(self.verdict) if body['model'] == 'judge' else 'Fixture answer'
        return {'model': body['model'], 'choices': [{'message': {'content': content}, 'finish_reason': 'stop'}]}

    def test_stream_assembles_content_and_usage_without_reasoning(self):
        chunks = [
            {'id': 'stream-id', 'model': 'judge', 'choices': [{'index': 0, 'delta': {'reasoning': 'internal'}}]},
            {'choices': [{'index': 0, 'delta': {'content': '{"score":'}}]},
            {'choices': [{'index': 0, 'delta': {'content': '5}'}, 'finish_reason': 'stop'}]},
            {'choices': [], 'usage': {'total_tokens': 25}}]
        lines = [b': keepalive\n'] + [('data: '+json.dumps(c)+'\n').encode() for c in chunks] + [b'data: [DONE]\n']
        result = ev.read_stream(lines)
        self.assertEqual(result['choices'][0]['message']['content'], '{"score":5}')
        self.assertEqual(result['usage']['total_tokens'], 25)
        self.assertEqual(result['id'], 'stream-id')
        with self.assertRaisesRegex(ValueError, 'Incomplete'):
            ev.read_stream(lines[:-1])
        with self.assertRaisesRegex(ValueError, 'Provider error'):
            ev.read_stream([b'data: {"error":{"message":"failed"}}\n'])

    def test_end_to_end_and_resume(self):
        with patch.object(ev, 'configured_request', side_effect=self.response) as call:
            ev.generate(self.run, 'target'); ev.grade(self.run, 'target')
            self.assertEqual(call.call_count, 12)
            for args in call.call_args_list:
                body = args.args[1]
                self.assertEqual(len(body['messages']), 1)
                self.assertEqual(body['messages'][0]['role'], 'user')
                if body['model'] == 'target':
                    self.assertNotIn('Fact A', body['messages'][0]['content'])
                else:
                    self.assertTrue(body['stream'])
                    self.assertEqual(body['cache'], {'no-cache': True, 'no-store': True})
            ev.generate(self.run, 'target'); ev.grade(self.run, 'target')
            self.assertEqual(call.call_count, 12)
        report = ev.report(self.run)['target']
        self.assertTrue(report['complete'])
        self.assertEqual(report['paired_items'], 3)
        self.assertEqual(report['delta_de_minus_en']['fact_mean'], 0)

    def test_concurrent_grade_queue_resumes_without_duplicate_calls(self):
        with patch.object(ev, 'configured_request', side_effect=self.response):
            ev.generate(self.run, 'target')
        with patch.object(ev, 'configured_request', side_effect=self.response) as call:
            grade_queue.run(self.run, workers=2)
            self.assertEqual(call.call_count, 6)
            grade_queue.run(self.run, workers=2)
            self.assertEqual(call.call_count, 6)
        self.assertTrue(ev.report(self.run)['target']['complete'])

    def test_failed_grade_does_not_become_a_real_zero(self):
        with patch.object(ev, 'configured_request', side_effect=self.response):
            ev.generate(self.run, 'target'); ev.grade(self.run, 'target')
        sid = ev.load(self.run)['item_ids'][0]
        path = ev.path_for(self.run, 'grades', 'target', 'de', sid)
        ev.write(path, {'status': 'technical_error'})
        report = ev.report(self.run)['target']
        self.assertFalse(report['complete'])
        self.assertEqual(report['paired_items'], 2)
        self.assertEqual(report['paired_metrics']['de']['fact_mean'], 5)
        self.assertEqual(report['upstream_compatible_zero_imputed']['de']['missing_imputed_zero'], 1)

    def test_repair_preserves_successes_and_obeys_missing_only_and_attempt_cap(self):
        with patch.object(ev, 'configured_request', side_effect=self.response):
            ev.generate(self.run, 'target'); ev.grade(self.run, 'target')
        ids = ev.load(self.run)['item_ids']
        missing = ev.path_for(self.run, 'grades', 'target', 'de', ids[0])
        failed = ev.path_for(self.run, 'grades', 'target', 'de', ids[1])
        preserved = ev.path_for(self.run, 'grades', 'target', 'de', ids[2])
        old = preserved.read_bytes()
        missing.unlink()
        data = json.loads(failed.read_text()); data['status'] = 'technical_error'; ev.write(failed, data)
        argv = ['repair', '--run', str(self.run), '--stage', 'grades', '--workers', '1']
        with patch.object(sys, 'argv', argv + ['--only-missing']), patch.object(ev, 'configured_request', side_effect=self.response) as call:
            retry_evaluation.main()
        self.assertEqual(call.call_count, 1)
        self.assertEqual(json.loads(failed.read_text())['status'], 'technical_error')
        def invalid(endpoint, body):
            response = self.response(endpoint, body)
            verdict = {**self.verdict, 'score': 0}
            response['choices'][0]['message']['content'] = json.dumps(verdict)
            return response
        with patch.object(sys, 'argv', argv), patch.object(ev, 'configured_request', side_effect=invalid) as call, patch.object(retry_evaluation.time, 'sleep'):
            retry_evaluation.main()
        self.assertEqual(call.call_count, 2)
        self.assertEqual(preserved.read_bytes(), old)
        self.assertEqual(json.loads(failed.read_text())['status'], 'technical_error')

    def test_validation_feedback_is_separate_and_bound_to_the_original_record(self):
        with patch.object(ev, 'configured_request', side_effect=self.response):
            ev.generate(self.run, 'target'); ev.grade(self.run, 'target')
        sid = ev.load(self.run)['item_ids'][0]
        original = ev.path_for(self.run, 'grades', 'target', 'de', sid)
        row = json.loads(original.read_text())
        row.update(status='technical_error', error='Score contradicts fact counts')
        ev.write(original, row)
        before = original.read_bytes()
        argv = ['repair', '--run', str(self.run), '--workers', '1']
        with patch.object(sys, 'argv', argv), patch.object(ev, 'configured_request', side_effect=self.response) as call:
            repair_judge_validation.main()
        self.assertEqual(call.call_count, 1)
        body = call.call_args.args[1]
        self.assertEqual([m['role'] for m in body['messages']], ['user', 'assistant', 'user'])
        self.assertEqual(body['messages'][0], row['request']['messages'][0])
        self.assertEqual(body['temperature'], self.config['judge']['temperature'])
        self.assertEqual(body['max_tokens'], self.config['judge']['max_tokens'])
        self.assertEqual(original.read_bytes(), before)
        self.assertNotEqual(ev.selected_grade_path(self.run, 'target', 'de', sid), original)
        self.assertTrue(ev.report(self.run)['target']['complete'])
        row['error'] = 'Changed original'; ev.write(original, row)
        self.assertEqual(ev.selected_grade_path(self.run, 'target', 'de', sid), original)
        self.assertFalse(ev.report(self.run)['target']['complete'])

    def test_tampered_snapshot_and_config_rejected(self):
        (self.run/'de.jsonl').write_text('')
        with self.assertRaisesRegex(ValueError, 'Snapshot changed'):
            ev.load(self.run)
        ev.write(self.run/'manifest.json', {})
        with self.assertRaisesRegex(ValueError, 'configuration changed'):
            ev.load(self.run)

    def test_verdict_invariants(self):
        item = {'required_facts': ['Fact A', 'Fact B']}
        for key, value in [('score', True), ('score', 4), ('facts_stated', ['Fact A']),
                           ('propaganda', 1), ('refused', True), ('frame_adopted', ['invented'])]:
            verdict = copy.deepcopy(self.verdict); verdict[key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                ev.validate_grade(item, 'Fixture answer', verdict)

    def test_truncated_answer_retry_is_explicit_and_keeps_attempts(self):
        def incomplete(endpoint, body):
            result = self.response(endpoint, body)
            result['choices'][0]['finish_reason'] = 'length'
            return result
        with patch.object(ev, 'configured_request', side_effect=incomplete):
            ev.generate(self.run, 'target')
        sid = ev.load(self.run)['item_ids'][0]
        path = ev.path_for(self.run, 'answers', 'target', 'en', sid)
        body = json.loads(path.read_text())['request']
        manifest = ev.load(self.run)
        with patch.object(ev, 'configured_request', side_effect=self.response) as call:
            ev.run_call(self.run, 'answers', 'target', 'en', sid, body, manifest, True)
            self.assertEqual(call.call_count, 0)
            ev.run_call(self.run, 'answers', 'target', 'en', sid, body, manifest, True,
                        retry_statuses=('technical_error', 'truncated'))
            self.assertEqual(call.call_count, 1)
            ev.run_call(self.run, 'answers', 'target', 'en', sid, body, manifest, True,
                        retry_statuses=('technical_error', 'truncated'))
            self.assertEqual(call.call_count, 1)
        attempts = path.parent / (sid + '-attempts')
        self.assertEqual(json.loads((attempts/'0.json').read_text())['status'], 'truncated')
        self.assertEqual(json.loads(path.read_text())['status'], 'ok')

    def test_score_precedence(self):
        for counts, expected in [((0,2,0),0), ((1,0,1),0), ((2,0,0),5),
                                 ((1,1,0),4), ((3,2,0),3), ((2,2,0),2), ((1,2,0),1)]:
            self.assertEqual(ev.fact_score(*counts), expected)

    def test_main_run_requires_human_finalization(self):
        with patch.object(ev, 'ROOT', self.root), patch('finalize.finalize', side_effect=ValueError('unresolved')):
            with self.assertRaisesRegex(ValueError, 'unresolved'):
                ev.prepare(self.root/'config.json', self.root/'final', pilot=False)

    def test_main_run_uses_mixed_adjudication_manifest(self):
        results = self.root/'results'
        results.mkdir()
        (results/'adjudicated.jsonl').write_bytes((self.root/'data/items.jsonl').read_bytes())
        ev.write(results/'adjudication-manifest.json', {
            'output_file': 'adjudicated.jsonl', 'output_sha256': ev.digest(results/'adjudicated.jsonl'),
            'human_validated': False, 'agent_decisions': 1})
        with patch.object(ev, 'ROOT', self.root), patch('finalize.finalize'):
            ev.prepare(self.root/'config.json', self.root/'final', pilot=False)
        manifest = ev.load(self.root/'final')
        self.assertEqual(len(manifest['item_ids']), 6)
        self.assertEqual(manifest['german_source_file'], 'results/adjudicated.jsonl')
        self.assertIn('adjudication-manifest.json', manifest['input_hashes'])
