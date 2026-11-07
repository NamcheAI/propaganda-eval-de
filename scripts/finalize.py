#!/usr/bin/env python3
"""Apply explicit human field decisions; fail closed on pending or conflicting issues."""
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path

from run import ROOT, build_queue, check_result, field_value, jsonl, write
from common import FIELDS, validate
from validate import validate_run


def read(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def finalize(run):
    validate_run(run, require_review=True)
    source = read(ROOT / "upstream/data/items.jsonl")
    config = json.loads((run / "config.json").read_text())
    if hashlib.sha256((ROOT / "upstream/data/items.jsonl").read_bytes()).hexdigest() != config["source_sha256"]:
        raise ValueError("Source hash changed")
    rows = read(run / "translated.jsonl")
    reviews = read(run / "reviews.jsonl")
    if [r["id"] for r in rows] != [r["id"] for r in source] or [r["id"] for r in reviews] != [r["id"] for r in source]:
        raise ValueError("Full translation and review of all source items required")
    queue = read(run / "human-review-queue.jsonl")
    translations = read(run / "translation-notes.jsonl")
    inputs = [{"id": s["id"], **{f: s[f] for f in FIELDS if f in s}} for s in source]
    check_result("translate", {"items": inputs}, {"items": translations})
    check_result("review", {"items": [{"source": s, **t} for s,t in zip(inputs, translations)]},
                 {"items": reviews})
    if rows != [{**s, **t["translation"]} for s,t in zip(source, translations)]:
        raise ValueError("Translation snapshot differs from recorded output")
    if queue != build_queue(source, translations, reviews):
        raise ValueError("Review queue differs from recorded findings")
    decisions = read(run / "human-decisions.jsonl")
    issues = {q["issue_id"]: q for q in queue}
    if len(issues) != len(queue):
        raise ValueError("Duplicate issue IDs")
    by_id = {r["id"]: r for r in rows}
    resolved, changes = set(), {}
    for d in decisions:
        issue_id = d["issue_id"]
        if issue_id not in issues or issue_id in resolved:
            raise ValueError("Unknown or duplicate decision")
        if d["decision"] not in ("accept", "reject", "modify"):
            raise ValueError("Pending/deferred decision blocks finalization")
        for key in ("reviewer", "reviewer_role", "reason", "final_text"):
            if not isinstance(d.get(key), str) or not d[key].strip():
                raise ValueError("Missing decision field: " + key)
        if datetime.fromisoformat(d["decided_at"]).utcoffset() is None:
            raise ValueError("Decision date must include timezone")
        if not isinstance(d.get("evidence"), list):
            raise ValueError("Missing evidence list")
        q = issues[issue_id]
        location = (q["item_id"], q["field"], q["index"])
        before = field_value(by_id[q["item_id"]], q["field"], q["index"])
        if before != q["translation"]:
            raise ValueError("Stale decision target")
        if location in changes and changes[location] != d["final_text"]:
            raise ValueError("Conflicting decisions for one field")
        changes[location] = d["final_text"]
        resolved.add(issue_id)
    if resolved != set(issues):
        raise ValueError(f"{len(set(issues) - resolved)} unresolved issues")
    for (sid, field, index), text in changes.items():
        if index is None:
            by_id[sid][field] = text
        else:
            by_id[sid][field][index] = text
    for original, target in zip(source, rows):
        validate({k:v for k,v in original.items() if k in FIELDS or k == "id"},
                 {k:v for k,v in target.items() if k in FIELDS or k == "id"})
        if {k:v for k,v in original.items() if k not in FIELDS} != {k:v for k,v in target.items() if k not in FIELDS}:
            raise ValueError("Metadata changed")
    jsonl(run / "human-adjudicated.jsonl", rows)
    write(run / "adjudication-manifest.json", {"resolved_issues": len(resolved),
          "changed_fields": len(changes), "scope": "Flagged cases only, not representative validation",
          "input_hashes": {name: hashlib.sha256((run / name).read_bytes()).hexdigest() for name in
              ("translated.jsonl", "reviews.jsonl", "human-review-queue.jsonl", "human-decisions.jsonl")},
          "output_sha256": hashlib.sha256((run / "human-adjudicated.jsonl").read_bytes()).hexdigest()})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    finalize(parser.parse_args().run_dir)
