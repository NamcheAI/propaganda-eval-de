import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from decision_ledger import load_decisions
from number_policy import working_rows
from review_ui import ReviewStore


class DecisionLedgerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.issues = [dict(issue_id=i, item_id='item', field='prompt', index=None,
                            source='1,234 people', translation='1,234 Leute') for i in ('a', 'b')]
        self.agent = dict(issue_id='a', decision='modify', final_text='1.234 Personen',
                          reason='Source checked', reviewer='Codex', reviewer_role='AI', evidence=[])
        self.write('human-decisions.jsonl', [])
        self.write('human-review-queue.jsonl', self.issues)
        self.write('agent-decisions.jsonl', [self.agent])

    def write(self, name, rows):
        (self.root / name).write_text(''.join(json.dumps(r) + '\n' for r in rows))

    def test_agent_applies_without_mutating_human_ledger(self):
        before = (self.root / 'human-decisions.jsonl').read_bytes()
        decisions = load_decisions(self.root, self.issues)
        rows = working_rows([{'id': 'item', 'prompt': '1,234 people'}],
                            [{'id': 'item', 'prompt': '1,234 Leute'}], self.issues, decisions)
        self.assertEqual(rows[0]['prompt'], '1.234 Personen')
        self.assertEqual(decisions[0]['decision_origin'], 'agent')
        self.assertEqual((self.root / 'human-decisions.jsonl').read_bytes(), before)

    def test_human_same_issue_overrides_even_when_deferred(self):
        self.write('human-decisions.jsonl', [{**self.agent, 'decision': 'defer', 'final_text': None}])
        decisions = load_decisions(self.root, self.issues)
        self.assertEqual(len(decisions), 1)
        self.assertEqual(decisions[0]['decision'], 'defer')
        self.assertEqual(decisions[0]['decision_origin'], 'human')

    def test_different_human_field_choice_reopens_agent_finding(self):
        self.write('human-decisions.jsonl', [{**self.agent, 'issue_id': 'b', 'final_text': '1.234 Menschen'}])
        before = (self.root / 'agent-decisions.jsonl').read_bytes()
        decisions = load_decisions(self.root, self.issues)
        self.assertEqual(decisions[0]['decision'], 'defer')
        self.assertTrue(decisions[0]['superseded_by_human_field'])
        self.assertEqual((self.root / 'agent-decisions.jsonl').read_bytes(), before)

    def test_compatible_human_field_choice_keeps_agent_decision(self):
        self.write('human-decisions.jsonl', [{**self.agent, 'issue_id': 'b', 'final_text': '1,234 Personen'}])
        self.assertEqual(load_decisions(self.root, self.issues)[0]['decision'], 'modify')

    def test_human_defer_blocks_agent_sibling_field_edit(self):
        self.write('human-decisions.jsonl', [{**self.agent, 'issue_id': 'b', 'decision': 'defer', 'final_text': None}])
        self.assertEqual(load_decisions(self.root, self.issues)[0]['decision'], 'defer')

    def test_revision_changes_with_agent_ledger(self):
        store = ReviewStore(self.root)
        before = store.revision()
        self.write('agent-decisions.jsonl', [{**self.agent, 'reason': 'Updated research'}])
        self.assertNotEqual(before, store.revision())

    def test_editorial_correction_preserves_human_record_and_is_exact(self):
        self.write('agent-decisions.jsonl', [])
        self.write('human-decisions.jsonl', [self.agent])
        before = (self.root / 'human-decisions.jsonl').read_bytes()
        self.write('editorial-corrections.jsonl', [dict(id='grammar', item_id='item',
            field='prompt', index=None, before='1.234 Personen', after='1.234 Menschen',
            reviewer='Codex', reviewer_role='Editorial', reason='Grammar', decided_at='2026-11-08T00:00:00+00:00')])
        result = load_decisions(self.root, self.issues)[0]
        self.assertEqual(result['final_text'], '1.234 Menschen')
        self.assertEqual(result['decision_origin'], 'agent')
        self.assertEqual((self.root / 'human-decisions.jsonl').read_bytes(), before)
        self.write('human-decisions.jsonl', [{**self.agent, 'final_text': 'Neue menschliche Fassung'}])
        self.assertEqual(load_decisions(self.root, self.issues)[0]['final_text'], 'Neue menschliche Fassung')

    def test_unknown_or_duplicate_agent_ids_fail_closed(self):
        for rows in ([self.agent, self.agent], [{**self.agent, 'issue_id': 'unknown'}]):
            self.write('agent-decisions.jsonl', rows)
            with self.assertRaisesRegex(ValueError, 'Unknown or duplicate'):
                load_decisions(self.root, self.issues)


if __name__ == '__main__':
    unittest.main()
