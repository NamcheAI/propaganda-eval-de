import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('translate', Path(__file__).resolve().parents[1] / 'scripts/common.py')
translate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(translate)


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.source = {'id': '0013', 'prompt': 'A question', 'required_facts': ['One', 'Two']}
        self.target = {'id': '0013', 'prompt': 'Eine Frage', 'required_facts': ['Eins', 'Zwei']}

    def test_preserves_string_ids(self):
        translate.validate(self.source, self.target)
        self.target['id'] = 13
        with self.assertRaises(ValueError):
            translate.validate(self.source, self.target)

    def test_missing_fact_rejected(self):
        self.target['required_facts'].pop()
        with self.assertRaises(ValueError):
            translate.validate(self.source, self.target)

    def test_added_explanation_field_rejected(self):
        self.target['explanation'] = 'Not permitted'
        with self.assertRaises(ValueError):
            translate.validate(self.source, self.target)

    def test_empty_translation_rejected(self):
        self.target['prompt'] = ''
        with self.assertRaises(ValueError):
            translate.validate(self.source, self.target)

    def test_gateway_closing_delimiter(self):
        self.assertEqual(translate.parse_response('{"items": []}</final'), {'items': []})

    def test_unexpected_trailing_output_rejected(self):
        with self.assertRaises(ValueError):
            translate.parse_response('{"items": []} additional answer')

    def test_invalid_json_is_not_repaired(self):
        with self.assertRaises(ValueError):
            translate.parse_response('{"items": [broken]}')

    def test_single_redundant_terminal_brace(self):
        self.assertEqual(translate.parse_response('{"items": [{"id":"1"}}]}'),
                         {'items': [{'id': '1'}]})


if __name__ == '__main__':
    unittest.main()
