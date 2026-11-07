import json
import sys
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from subscription import invoke, TransportError
from run import split_review, restore_quote_whitespace


class SubscriptionTest(unittest.TestCase):
    @patch('subscription.subprocess.run')
    def test_isolation_and_exact_prompt(self, run):
        model = 'anthropic/claude-fable-5-1'
        run.return_value = SimpleNamespace(returncode=0, stdout=json.dumps({
            'result': '{}', 'modelUsage': {model: {}}, 'is_error': False}))
        with patch.dict('os.environ', {'ANTHROPIC_AUTH_TOKEN': 'local-token',
                                     'CLAUDE_CODE_OAUTH_TOKEN': 'other-token'}):
            invoke(model, 'medium', 'exact prompt', {'items': []}, 'gateway-key')
        args, kwargs = run.call_args
        self.assertEqual(args[0][-1], 'exact prompt')
        self.assertIn('--bare', args[0])
        self.assertIn('--safe-mode', args[0])
        self.assertEqual(args[0][args[0].index('--tools') + 1], '')
        self.assertEqual(json.loads(kwargs['input']), {'items': []})
        self.assertNotIn('ANTHROPIC_AUTH_TOKEN', kwargs['env'])
        self.assertNotIn('CLAUDE_CODE_OAUTH_TOKEN', kwargs['env'])
        self.assertEqual(kwargs['env']['ANTHROPIC_API_KEY'], 'gateway-key')

    @patch('subscription.subprocess.run')
    def test_provider_failure_is_not_schema_error(self, run):
        run.return_value = SimpleNamespace(returncode=1, stdout=json.dumps({
            'is_error': True, 'result': '429 secret-key'}))
        with self.assertRaises(TransportError) as caught:
            invoke('requested', 'medium', 'prompt', {}, 'secret-key')
        self.assertNotIn('secret-key', str(caught.exception))

    @patch('subscription.subprocess.run')
    def test_wrong_model_rejected(self, run):
        run.return_value = SimpleNamespace(returncode=0, stdout=json.dumps({
            'result': '{}', 'modelUsage': {'unexpected': {}}}))
        with self.assertRaisesRegex(ValueError, 'Unexpected returned model'):
            invoke('requested', 'medium', 'prompt', {}, 'key')


class SplitReviewTest(unittest.TestCase):
    @patch('run.call_subscription')
    def test_split_preserves_order_text_and_prompt(self, call):
        call.side_effect = lambda payload, prompt, key: {'output': payload}
        items = [{'id': str(i), 'text': 'unchanged'} for i in range(5)]
        result = split_review({'items': items}, 'exact prompt', 'key')
        self.assertEqual(result['output']['items'], items)
        self.assertEqual([len(c.args[0]['items']) for c in call.call_args_list], [2, 3])
        self.assertTrue(all(c.args[1] == 'exact prompt' for c in call.call_args_list))


class QuoteWhitespaceTest(unittest.TestCase):
    def test_only_whitespace_is_restored(self):
        payload = {'items': [{'source': {'prompt': 'One\u2002two'},
                              'translation': {'prompt': 'Eins zwei'}}]}
        finding = {'field': 'prompt', 'index': None, 'source': 'One two',
                   'translation': 'Eins drei'}
        output = {'items': [{'findings': [finding]}]}
        self.assertEqual(restore_quote_whitespace(payload, output), 1)
        self.assertEqual(finding['source'], 'One\u2002two')
        self.assertEqual(finding['translation'], 'Eins drei')
