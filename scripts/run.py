#!/usr/bin/env python3
"""Translate with Astra and review with Fable; keep human decisions separate."""
import argparse
from collections import Counter
import concurrent.futures
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import hashlib
import json
import os
import re
import random
import threading
from pathlib import Path
import time
import urllib.error
import urllib.request

from common import FIELDS, parse_response, validate

ROOT = Path(__file__).resolve().parents[1]
MODELS = {"translate": ("chatgpt/gpt-6-astra", "high"),
          "review": ("anthropic/claude-fable-5-1", "medium")}


def sha(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    temp.replace(path)


def jsonl(path, rows):
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))


def load_key():
    # Read dotenv as data, never execute shell statements from it.
    values = {}
    if (ROOT / ".env").exists():
        for line in (ROOT / ".env").read_text().splitlines():
            if line.strip() and not line.lstrip().startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                values[key.strip()] = value.strip().strip("\"'")
    return values.get("INFERENCE_API_KEY") or os.environ["INFERENCE_API_KEY"]


def retry_delay(headers, attempt):
    value = headers.get("retry-after") or headers.get("llm_provider-retry-after")
    if value:
        try:
            return max(0.0, float(value))
        except ValueError:
            try:
                return max(0.0, (parsedate_to_datetime(value) - datetime.now(timezone.utc)).total_seconds())
            except (ValueError, TypeError):
                pass
    return min(60.0, 15 * 2 ** (attempt - 1)) + random.uniform(0, 1)


def field_value(row, field, index):
    if field not in FIELDS or field not in row:
        raise ValueError("Unknown field")
    value = row[field]
    if isinstance(value, list):
        if type(index) is not int or not 0 <= index < len(value):
            raise ValueError("Invalid list index")
        return value[index]
    if index is not None:
        raise ValueError("Scalar field with index")
    return value


def check_annotation(note, source, target, review=False):
    for key in ("field", "index", "source", "translation", "reason", "needs_human_review"):
        if key not in note:
            raise ValueError("Missing annotation key: " + key)
    if note["source"] != field_value(source, note["field"], note["index"]):
        raise ValueError("Annotation source is not exact field text")
    if note["translation"] != field_value(target, note["field"], note["index"]):
        raise ValueError("Annotation target is not exact field text")
    if not isinstance(note["reason"], str) or not note["reason"].strip():
        raise ValueError("Missing reason")
    if type(note["needs_human_review"]) is not bool:
        raise ValueError("Invalid human review flag")
    if review:
        if note.get("category") not in ("error", "tradeoff", "style"):
            raise ValueError("Invalid category")
        if note.get("severity") not in ("critical", "major", "minor", "none"):
            raise ValueError("Invalid severity")
        for key in ("suggestion", "uncertainty"):
            if key not in note or (note[key] is not None and
                                  (not isinstance(note[key], str) or not note[key].strip())):
                raise ValueError("Invalid " + key)


def check_result(mode, payload, result):
    outputs = result["items"]
    if len(outputs) != len(payload["items"]):
        raise ValueError("Wrong item count")
    for inp, out in zip(payload["items"], outputs):
        source = inp if mode == "translate" else inp["source"]
        target = out["translation"] if mode == "translate" else out["proposed_translation"]
        validate(source, target)
        if mode == "translate":
            if not isinstance(out.get("notes"), list):
                raise ValueError("Missing notes")
            for note in out["notes"]:
                check_annotation(note, source, target)
        else:
            if out["id"] != source["id"] or out.get("verdict") not in (
                    "usable", "local_corrections", "rework"):
                raise ValueError("Invalid review identity/verdict")
            if not isinstance(out.get("findings"), list):
                raise ValueError("Missing findings")
            for note in out["findings"]:
                check_annotation(note, source, inp["translation"], review=True)
            for field in FIELDS:
                if field not in source:
                    continue
                before, after = inp["translation"][field], target[field]
                pairs = enumerate(zip(before, after)) if isinstance(before, list) else [(None, (before, after))]
                for index, (old, new) in pairs:
                    if old != new and not any(n["field"] == field and n["index"] == index and
                                             n.get("suggestion") == new for n in out["findings"]):
                        raise ValueError("Undocumented reviewer change")


def call(mode, payload, prompt, directory, key):
    model, effort = MODELS[mode]
    body = {"model": model, "reasoning_effort": effort, "max_tokens": 24000,
            "messages": [{"role": "system", "content": prompt},
                         {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}],
            "response_format": {"type": "json_object"}}
    fingerprint = sha(body)
    cache = ROOT / "work/model-calls" / mode / fingerprint
    record_path = cache / "validated.json"
    if record_path.exists():
        record = json.loads(record_path.read_text())
        check_result(mode, payload, record["output"])
        return record
    write(cache / "request.json", body)
    for attempt in range(1, 5):
        delay = 2 ** attempt
        attempt_path = cache / f"attempt-{time.time_ns()}.json"
        started = datetime.now(timezone.utc).isoformat()
        try:
            request = urllib.request.Request("https://inference.namche.net/v1/chat/completions",
                data=json.dumps(body).encode(), headers={"Authorization": "Bearer " + key,
                "Content-Type": "application/json", "User-Agent": "curl/8.7.1"})
            with urllib.request.urlopen(request, timeout=900) as response:
                data = json.load(response)
            choice = data["choices"][0]
            record = {"request_sha256": fingerprint, "started_at": started,
                      "completed_at": datetime.now(timezone.utc).isoformat(),
                      "requested_model": model, "requested_reasoning_effort": effort,
                      "returned_model": data.get("model"), "response_id": data.get("id"),
                      "usage": data.get("usage"), "system_fingerprint": data.get("system_fingerprint"),
                      "finish_reason": choice.get("finish_reason"),
                      "content": choice["message"].get("content")}
            write(attempt_path, record)
            if choice.get("finish_reason") not in ("stop", "end_turn"):
                raise ValueError("Incomplete response: " + str(choice.get("finish_reason")))
            record["output"] = parse_response(record["content"])
            check_result(mode, payload, record["output"])
            write(record_path, record)
            return record
        except urllib.error.HTTPError as exc:
            # Do not persist headers or credentials, including in error output.
            headers = {k.lower(): v for k,v in exc.headers.items()}
            allowed = {k:v for k,v in headers.items() if k in
                       ("retry-after", "request-id", "llm_provider-retry-after",
                        "llm_provider-request-id", "llm_provider-x-should-retry") or
                       k.startswith(("anthropic-ratelimit-", "llm_provider-anthropic-ratelimit-"))}
            write(attempt_path, {"started_at": started, "http_status": exc.code, "headers": allowed})
            if exc.code in (400, 401, 403, 404):
                raise RuntimeError(f"{mode}: HTTP {exc.code}; no fallback model") from None
            if exc.code == 429:
                delay = retry_delay(headers, attempt)
                if delay > 120:
                    raise RuntimeError(f"{mode}: provider requests {delay:.0f}s wait; resume later") from None
            error = f"HTTP {exc.code}"
        except (ValueError, KeyError, TypeError, TimeoutError, urllib.error.URLError) as exc:
            error = type(exc).__name__ + ": " + str(exc)
        print(f"{mode} {payload['items'][0].get('id', '')}: attempt {attempt}: {error}", flush=True)
        if attempt == 4:
            raise RuntimeError(error)
        time.sleep(delay)


def export_batches(directory):
    manifest = directory / "batches.jsonl"
    existing = [json.loads(x) for x in manifest.read_text().splitlines()] if manifest.exists() else []
    rows = []
    for mode in MODELS:
        for path in sorted((ROOT / "work/model-calls" / mode).glob("*/validated.json")):
            record = json.loads(path.read_text())
            request = json.loads(path.with_name("request.json").read_text())
            if "messages" in request:
                prompt = request["messages"][0]["content"]
                payload = json.loads(request["messages"][1]["content"])
            else:
                prompt, payload = request["system"], request["payload"]
            usage = record.get("usage") or {}
            tokens = {"input_tokens": usage.get("prompt_tokens", sum(usage.get(k, 0) or 0 for k in
                       ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))),
                      "output_tokens": usage.get("completion_tokens", usage.get("output_tokens", 0))}
            rows.append({"mode": mode, "item_ids": [r.get("id", r.get("source", {}).get("id")) for r in payload["items"]],
                         "input_sha256": sha(payload), "output_sha256": sha(record["output"]),
                         "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                         "tokens": tokens,
                         **{k:record.get(k) for k in ("requested_model", "requested_reasoning_effort", "returned_model",
                                                     "started_at", "completed_at", "transport", "cli_version")}})
    merged = {(r["mode"], tuple(r["item_ids"])):r for r in existing}
    merged.update({(r["mode"], tuple(r["item_ids"])):r for r in rows})
    rows = list(merged.values())
    jsonl(manifest, rows)
    queue = [json.loads(x) for x in (directory / "human-review-queue.jsonl").read_text().splitlines()]
    status = json.loads((directory / "status.json").read_text())
    write(directory / "summary.json", {**status, "flagged_items": len({q["item_id"] for q in queue}),
          "issues_by_origin": dict(Counter(q["origin"] for q in queue)),
          "review_severities": dict(Counter(q.get("severity") for q in queue if q["origin"] == "reviewer")),
          "tokens": {mode: {key:sum(r["tokens"][key] for r in rows if r["mode"] == mode)
                            for key in ("input_tokens", "output_tokens")} for mode in MODELS}})


def build_queue(sources, translations, reviews):
    first = {r["translation"]["id"]: r for r in translations}
    checked = {r["id"]: r for r in reviews}
    topics = json.loads((ROOT / "results/expert-topics.json").read_text())
    queue = []
    for s in sources:
        sid = s["id"]
        notes = [("translator", n) for n in first.get(sid, {}).get("notes", [])
                 if n["needs_human_review"]]
        # All reviewer findings go to humans, even model-confident minor changes.
        notes += [("reviewer", n) for n in checked.get(sid, {}).get("findings", [])]
        if sid in first:
            target = first[sid]["translation"]
            for topic in topics:
                if topic["item_id"] == sid:
                    field, index = topic["field"], topic["index"]
                    notes.append(("domain_question", {"field": field, "index": index,
                        "source": field_value(s, field, index), "translation": field_value(target, field, index),
                        "reason": topic["question"],
                        "suggestion": None, "uncertainty": topic["question"], "needs_human_review": True}))
            for field in FIELDS:
                if field not in s:
                    continue
                pairs = (enumerate(zip(s[field], target[field])) if isinstance(s[field], list)
                         else [(None, (s[field], target[field]))])
                for index, (english, german) in pairs:
                    def literals(text):
                        return [Counter(re.findall(pattern, text)) for pattern in
                                (r"\d+(?:[.,]\d+)*", r"[\u3400-\u9fff]+", r"https?://[^\s<>\"]+")]
                    if literals(english) != literals(german):
                        notes.append(("literal_check", {"field": field, "index": index,
                            "source": english, "translation": german,
                            "reason": "Zahlen, chinesische Zeichen oder URLs weichen ab. Heuristischer Hinweis, kein bewiesener Bedeutungsfehler.",
                            "suggestion": None, "uncertainty": "Ist die Abweichung bedeutungstreu und beabsichtigt?",
                            "needs_human_review": True}))
        for origin, note in notes:
            entry = {"item_id": sid, "origin": origin, "source_url": s.get("source_url"), **note}
            entry["issue_id"] = sha(entry)
            entry["status"] = "pending"
            queue.append(entry)
    return queue


def export(directory, sources, translations, reviews):
    first = {r["translation"]["id"]: r for r in translations}
    checked = {r["id"]: r for r in reviews}
    jsonl(directory / "translated.jsonl", [{**s, **first[s["id"]]["translation"]}
                                            for s in sources if s["id"] in first])
    jsonl(directory / "review-proposed.jsonl", [{**s, **checked[s["id"]]["proposed_translation"]}
                                                 for s in sources if s["id"] in checked])
    jsonl(directory / "translation-notes.jsonl", translations)
    jsonl(directory / "reviews.jsonl", reviews)
    queue = build_queue(sources, translations, reviews)
    jsonl(directory / "human-review-queue.jsonl", queue)
    # An empty ledger never implies that pending issues were accepted.
    ledger = directory / "human-decisions.jsonl"
    if not ledger.exists():
        ledger.write_text("")
    report = ["# Expertenprüfung", "", "Status: maschineller Entwurf, keine menschliche Freigabe.", "",
              "Entscheidungen in human-decisions.jsonl dokumentieren; siehe METHOD.md.", ""]
    source_by_id = {s["id"]: s for s in sources}
    for q in queue:
        report += [f"## {q['item_id']} / {q['field']} / {q['index']}", "",
                   f"Issue-ID: `{q['issue_id']}`", "", f"Herkunft des Hinweises: `{q['origin']}`", "",
                   "Quelle des Benchmark-Falls: " + str(q.get("source_url") or "Nicht angegeben"), "",
                   "Original:", "", q["source"], "",
                   "Astra-Übersetzung:", "", q["translation"], "", "Begründung:", "", q["reason"], "",
                   "Vorschlag / Alternative:", "", str(q.get("suggestion") or q.get("alternative") or "Keiner"),
                   "", "Offene Frage:", "", str(q.get("uncertainty") or "Siehe Begründung"), "",
                   "<details><summary>Vollständiger Fall als Kontext (EN und DE)</summary>", "", "```json",
                   json.dumps({"source": source_by_id[q["item_id"]],
                               "translation": first[q["item_id"]]["translation"]}, ensure_ascii=False, indent=2),
                   "```", "", "</details>", ""]
    (directory / "HUMAN_REVIEW.md").write_text("\n".join(report))
    write(directory / "status.json", {"source_items": len(sources), "translated": len(first),
          "reviewed": len(checked), "pending_issues": len(queue), "human_validated": False})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, default=ROOT / "results")
    parser.add_argument("--batch-size", type=int, default=5)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--translate-only", action="store_true")
    args = parser.parse_args()
    if args.batch_size < 1 or args.workers < 1 or (args.limit is not None and args.limit < 1):
        parser.error("Counts must be positive")
    source_path = ROOT / "upstream/data/items.jsonl"
    sources = [json.loads(line) for line in source_path.read_text().splitlines()]
    if args.limit:
        sources = sources[:args.limit]
    inputs = [{"id": s["id"], **{f: s[f] for f in FIELDS if f in s}} for s in sources]
    prompts = {mode: (ROOT / f"prompts/{mode}.md").read_text() for mode in MODELS}
    config = {"source_sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
              "models": MODELS, "prompt_sha256": {k: hashlib.sha256(v.encode()).hexdigest() for k,v in prompts.items()},
              "batch_size": args.batch_size, "item_ids": [s["id"] for s in sources],
              "endpoint": "https://inference.namche.net/v1/chat/completions",
              "max_tokens": 24000, "sampling": "provider defaults; temperature/top_p/seed not set",
              "response_format": {"type": "json_object"}, "review_transport": "gateway", "provider_prompt_sha256": {"translate": hashlib.sha256((ROOT / "prompts/translate-provider.txt").read_bytes()).hexdigest()}}
    config_path = args.run_dir / "config.json"
    if config_path.exists() and sha(json.loads(config_path.read_text())) != sha(config):
        raise ValueError("Run configuration changed; use a new directory")
    write(config_path, config)
    batches = [inputs[i:i+args.batch_size] for i in range(0, len(inputs), args.batch_size)]
    review_slot = threading.Semaphore(args.workers)
    failed = threading.Event()
    known_path = args.run_dir / "translation-notes.jsonl"
    known = {r["translation"]["id"]:r for r in map(json.loads, known_path.read_text().splitlines())} if known_path.exists() else {}
    key = None if args.translate_only and all(s["id"] in known for s in sources) else load_key()

    def run(batch):
        if failed.is_set():
            raise RuntimeError("Stopped after previous batch failure; resume from cache")
        first = ([known[s["id"]] for s in batch] if all(s["id"] in known for s in batch) else
                 call("translate", {"items": batch}, prompts["translate"], args.run_dir, key)["output"]["items"])
        print(f"translated {batch[0]['id']}..{batch[-1]['id']}", flush=True)
        review = []
        if not args.translate_only:
            payload = {"items": [{"source": s, **t} for s,t in zip(batch, first)]}
            with review_slot:
                if failed.is_set():
                    raise RuntimeError("Review stopped after previous failure")
                try:
                    review = call("review", payload, prompts["review"], args.run_dir, key)["output"]["items"]
                except Exception:
                    failed.set()
                    raise
            print(f"reviewed {batch[0]['id']}..{batch[-1]['id']}", flush=True)
        return first, review

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(run, batch): i for i, batch in enumerate(batches)}
        for future in concurrent.futures.as_completed(futures):
            try:
                results.append((futures[future], future.result()))
            except Exception:
                failed.set()
                for other in futures:
                    other.cancel()
                raise
            ordered = [r for _, r in sorted(results)]
            known.update({x["translation"]["id"]:x for r in ordered for x in r[0]})
            export(args.run_dir, sources, [known[s["id"]] for s in sources if s["id"] in known],
                   [x for r in ordered for x in r[1]])
            export_batches(args.run_dir)
    print("Candidate complete; human decisions required before release.", flush=True)


if __name__ == "__main__":
    main()
