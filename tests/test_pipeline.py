import copy
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
import hashlib
import json

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from run import build_queue, check_result, export, field_value, jsonl, retry_delay, write
import finalize as finalizer


class TranslationV2Tests(unittest.TestCase):
    def test_retry_after_takes_precedence(self):
        self.assertEqual(retry_delay({"retry-after": "90"}, 1), 90)
        self.assertEqual(retry_delay({"llm_provider-retry-after": "42"}, 1), 42)
        with patch("run.random.uniform", return_value=0):
            self.assertEqual(retry_delay({}, 1), 15)
            self.assertEqual(retry_delay({}, 3), 60)

    def setUp(self):
        self.source = {"id": "0013", "prompt": "Who?", "required_facts": ["One", "Two"]}
        self.target = {"id": "0013", "prompt": "Wer?", "required_facts": ["Eins", "Zwei"]}
        self.payload = {"items": [{"source": self.source, "translation": self.target, "notes": []}]}
        self.result = {"items": [{"id": "0013", "verdict": "usable", "findings": [],
                                    "proposed_translation": copy.deepcopy(self.target)}]}

    def test_unchanged_review(self):
        check_result("review", self.payload, self.result)

    def test_undocumented_change_rejected(self):
        self.result["items"][0]["proposed_translation"]["prompt"] = "Warum?"
        with self.assertRaisesRegex(ValueError, "Undocumented"):
            check_result("review", self.payload, self.result)

    def test_documented_change(self):
        item = self.result["items"][0]
        item["proposed_translation"]["prompt"] = "Wer genau?"
        item["findings"] = [{"field": "prompt", "index": None, "source": "Who?",
            "translation": "Wer?", "reason": "Test", "category": "error", "severity": "minor",
            "suggestion": "Wer genau?", "uncertainty": None, "needs_human_review": False}]
        check_result("review", self.payload, self.result)
        item["findings"][0]["translation"] = "stale"
        with self.assertRaisesRegex(ValueError, "exact field"):
            check_result("review", self.payload, self.result)

    def test_negative_and_boolean_indices_rejected(self):
        for index in (-1, True, 2):
            with self.assertRaises(ValueError):
                field_value(self.source, "required_facts", index)

    def test_fact_removal_rejected(self):
        self.result["items"][0]["proposed_translation"]["required_facts"].pop()
        with self.assertRaises(ValueError):
            check_result("review", self.payload, self.result)

    def test_missing_uncertainty_flag_rejected(self):
        result = {"items": [{"translation": self.target, "notes": [{"field": "prompt"}]}]}
        with self.assertRaises(ValueError):
            check_result("translate", {"items": [self.source]}, result)

    def test_confident_minor_findings_still_need_humans(self):
        finding = {"field": "prompt", "index": None, "source": "Who?", "translation": "Wer?",
                   "reason": "Test", "severity": "minor", "needs_human_review": False}
        queue = build_queue([self.source], [{"translation": self.target, "notes": []}],
                            [{"id": "0013", "findings": [finding]}])
        self.assertEqual(len(queue), 1)
        self.assertEqual(queue[0]["status"], "pending")

    def test_finalization_requires_complete_consistent_human_decisions(self):
        note = {"field": "prompt", "index": None, "source": "Who?", "translation": "Wer?",
                "reason": "Context missing", "alternative": None, "needs_human_review": True}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "upstream/data").mkdir(parents=True)
            source_path = root / "upstream/data/items.jsonl"
            jsonl(source_path, [self.source])
            run = root / "run"
            run.mkdir()
            write(run / "config.json", {"source_sha256": hashlib.sha256(source_path.read_bytes()).hexdigest()})
            export(run, [self.source], [{"translation": self.target, "notes": [note]}], self.result["items"])
            with patch.object(finalizer, "ROOT", root), patch.object(finalizer, "validate_run"):
                with self.assertRaisesRegex(ValueError, "unresolved"):
                    finalizer.finalize(run)
                queue = finalizer.read(run / "human-review-queue.jsonl")
                jsonl(run / "human-review-queue.jsonl", [])
                with self.assertRaisesRegex(ValueError, "queue differs"):
                    finalizer.finalize(run)
                jsonl(run / "human-review-queue.jsonl", queue)
                decision = {"issue_id": queue[0]["issue_id"], "decision": "reject", "reviewer": "Test reviewer",
                            "reviewer_role": "Test fixture", "decided_at": "2026-11-07T12:00:00+00:00",
                            "reason": "Test only", "final_text": "Wer?", "evidence": []}
                jsonl(run / "human-decisions.jsonl", [decision])
                finalizer.finalize(run)
                self.assertEqual(finalizer.read(run / "human-adjudicated.jsonl"), [self.target])
                decision["decision"] = "defer"
                jsonl(run / "human-decisions.jsonl", [decision])
                with self.assertRaisesRegex(ValueError, "deferred"):
                    finalizer.finalize(run)


if __name__ == "__main__":
    unittest.main()
