import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from validate import validate_published


class ReleaseTest(unittest.TestCase):
    def test_frozen_release_and_raw_output_are_both_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run = root/'results'
            run.mkdir()
            (root/'data').mkdir()
            raw, final = b'{"prompt":"raw"}\n', b'{"prompt":"final"}\n'
            (run/'translated.jsonl').write_bytes(raw)
            (run/'adjudicated.jsonl').write_bytes(final)
            published = root/'data/items.jsonl'
            published.write_bytes(final)
            (run/'release-manifest.json').write_text(json.dumps({
                'status': 'final', 'data_sha256': hashlib.sha256(final).hexdigest(),
                'raw_translation_sha256': hashlib.sha256(raw).hexdigest()}))
            with patch('validate.ROOT', root):
                validate_published(run)
                published.write_bytes(b'{"prompt":"changed"}\n')
                with self.assertRaisesRegex(AssertionError, 'Published'):
                    validate_published(run)
                published.write_bytes(raw)
                with self.assertRaisesRegex(AssertionError, 'Published'):
                    validate_published(run)
                published.write_bytes(final)
                (run/'translated.jsonl').write_bytes(b'{"prompt":"changed raw"}\n')
                with self.assertRaisesRegex(AssertionError, 'Raw'):
                    validate_published(run)


if __name__ == '__main__':
    unittest.main()
