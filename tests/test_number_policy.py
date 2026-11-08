import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from number_policy import normalize, covered, literals_equal, working_rows
from run import build_queue


class NumberPolicyTests(unittest.TestCase):
    def test_formats_without_changing_values(self):
        for source, expected in [('1,234', '1.234'), ('1.23', '1,23'),
                                 ('1,234.56', '1.234,56'), ('1.951', '1,951'),
                                 ('42.1602', '42,1602'), ('1,234,567', '1.234.567'),
                                 ('-1.23%', '-1,23%')]:
            with self.subTest(source=source):
                self.assertEqual(normalize(source, source), expected)
                self.assertEqual(normalize(source, expected), expected)

    def test_protects_nonquantities_and_unmatched_values(self):
        for text in ['https://example.org/1.23', 'v1.23', '1.2.3',
                     '12.03.2026', 'Article 1.23', 'Version 1.23', '2026']:
            self.assertEqual(normalize(text, text), text)
        self.assertEqual(normalize('1,234', '1,235'), '1,235')
        self.assertEqual(normalize('1,234 and 1.234', '1,234 und 1.234'), '1,234 und 1.234')

    def test_preserves_real_mismatches(self):
        self.assertTrue(literals_equal('1,234.56 yuan', '1.234,56 Yuan'))
        self.assertFalse(literals_equal('1,234 yuan', '1.235 Yuan'))
        self.assertFalse(literals_equal('1,234 中', '1.234'))
        self.assertFalse(literals_equal('https://a/1.23', 'https://a/1,23'))

    def test_only_pure_format_proposals_are_covered(self):
        issue = {'issue_id': 'a', 'origin': 'reviewer', 'source': '1,234 yuan',
                 'translation': '1,234 Yuan', 'suggestion': '1.234 Yuan'}
        policy = {'reviewed_format_only_issue_ids': []}
        self.assertTrue(covered(issue, policy))
        self.assertFalse(covered({**issue, 'suggestion': '1.234 Euro'}, policy))
        self.assertFalse(covered({**issue, 'suggestion': None}, policy))
        self.assertFalse(covered({**issue, 'origin': 'human'}, policy))

    def test_future_literal_check_accepts_localization(self):
        source = {'id': 'test', 'prompt': '1,234.56 yuan'}
        translation = {'translation': {'id': 'test', 'prompt': '1.234,56 Yuan'}, 'notes': []}
        self.assertEqual(build_queue([source], [translation], [], number_policy=True), [])
        self.assertTrue(build_queue([source], [translation], []))

    def test_working_copy_keeps_human_wording_and_raw_records(self):
        source = [{'id': 'x', 'prompt': '1,234 people'}]
        raw = [{'id': 'x', 'prompt': '1,234 Personen'}]
        issue = {'issue_id': 'a', 'item_id': 'x', 'field': 'prompt', 'index': None,
                 'source': '1,234 people'}
        decisions = [{'issue_id': 'a', 'decision': 'modify', 'final_text': '1,234 Menschen'}]
        original = copy.deepcopy((raw, decisions))
        self.assertEqual(working_rows(source, raw, [issue], decisions)[0]['prompt'], '1.234 Menschen')
        self.assertEqual((raw, decisions), original)


if __name__ == '__main__':
    unittest.main()
