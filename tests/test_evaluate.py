import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import evaluate as ev


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
            ev.generate(self.run, 'target'); ev.grade(self.run, 'target')
            self.assertEqual(call.call_count, 12)
        report = ev.report(self.run)['target']
        self.assertTrue(report['complete'])
        self.assertEqual(report['paired_items'], 3)
        self.assertEqual(report['delta_de_minus_en']['fact_mean'], 0)

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

    def test_score_precedence(self):
        for counts, expected in [((0,2,0),0), ((1,0,1),0), ((2,0,0),5),
                                 ((1,1,0),4), ((3,2,0),3), ((2,2,0),2), ((1,2,0),1)]:
            self.assertEqual(ev.fact_score(*counts), expected)

    def test_main_run_requires_human_finalization(self):
        with patch.object(ev, 'ROOT', self.root), patch('finalize.finalize', side_effect=ValueError('unresolved')):
            with self.assertRaisesRegex(ValueError, 'unresolved'):
                ev.prepare(self.root/'config.json', self.root/'final', pilot=False)
