import json
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import generate_parallel as runner


class ParallelGenerationTest(unittest.TestCase):
    def test_resume_and_worker_bound(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            items = [{'id': str(i), 'prompt': 'test'} for i in range(4)]
            manifest = {'config': {'models': ['arete-27b'], 'generation': {}}}
            saved = runner.ev.path_for(root, 'answers', 'arete-27b', 'en', '0')
            saved.parent.mkdir(parents=True)
            saved.write_text(json.dumps({'status': 'ok'}))
            lock = threading.Lock()
            active = peak = 0
            calls = []

            def invoke(directory, stage, model, language, sid, body, meta, retry):
                nonlocal active, peak
                with lock:
                    active += 1
                    peak = max(peak, active)
                    calls.append((language, sid))
                time.sleep(0.01)
                with lock:
                    active -= 1
                return {'status': 'ok'}

            with patch.object(sys, 'argv', ['generate_parallel', '--run', str(root),
                    '--model', 'arete-27b', '--workers', '2']), \
                 patch.object(runner.ev, 'load', return_value=manifest), \
                 patch.object(runner.ev, 'read', return_value=items), \
                 patch.object(runner.ev, 'run_call', side_effect=invoke), \
                 patch.object(runner.ev, 'report'):
                runner.main()
            self.assertEqual(len(calls), 7)
            self.assertEqual(len(set(calls)), 7)
            self.assertNotIn(('en', '0'), calls)
            self.assertEqual(peak, 2)


if __name__ == '__main__':
    unittest.main()
