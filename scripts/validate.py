#!/usr/bin/env python3
"""Validate data, structural invariants, batch provenance and the human review queue."""
import argparse
import hashlib
import json
from pathlib import Path

from run import ROOT, build_queue, check_result, sha
from common import FIELDS


def read(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def validate_run(run, require_review=False):
    config = json.loads((run / 'config.json').read_text())
    source_path = ROOT / 'upstream/data/items.jsonl'
    assert hashlib.sha256(source_path.read_bytes()).hexdigest() == config['source_sha256'], 'Source hash'
    assert hashlib.sha256((ROOT / 'prompts/translate-provider.txt').read_bytes()).hexdigest() == config['provider_prompt_sha256']['translate'], 'Provider prompt hash'
    sources = read(source_path)
    assert [s['id'] for s in sources] == config['item_ids'], 'Source coverage'
    inputs = {s['id']: {'id':s['id'], **{f:s[f] for f in FIELDS if f in s}} for s in sources}
    translations = read(run / 'translation-notes.jsonl')
    check_result('translate', {'items':list(inputs.values())}, {'items':translations})
    assert read(run / 'translated.jsonl') == [{**s, **t['translation']} for s,t in zip(sources, translations)]
    assert read(ROOT / 'data/items.jsonl') == read(run / 'translated.jsonl'), 'Published translation mismatch'
    reviews = read(run / 'reviews.jsonl')
    if require_review:
        assert len(reviews) == len(sources), 'Incomplete review'
    tm = {t['translation']['id']:t for t in translations}
    rm = {r['id']:r for r in reviews}
    assert len(rm) == len(reviews), 'Duplicate reviews'
    seen = {'translate':set(), 'review':set()}
    for batch in read(run / 'batches.jsonl'):
        mode, ids = batch['mode'], batch['item_ids']
        assert not seen[mode].intersection(ids) and len(set(ids)) == len(ids), 'Duplicate batch items'
        seen[mode].update(ids)
        prompt = (ROOT / f'prompts/{mode}.md').read_text()
        assert hashlib.sha256(prompt.encode()).hexdigest() == batch['prompt_sha256'] == config['prompt_sha256'][mode]
        assert batch['requested_model'] == config['models'][mode][0]
        assert batch['requested_reasoning_effort'] == config['models'][mode][1]
        if mode == 'translate':
            payload = {'items':[inputs[sid] for sid in ids]}
            output = {'items':[tm[sid] for sid in ids]}
        else:
            payload = {'items':[{'source':inputs[sid], **tm[sid]} for sid in ids]}
            output = {'items':[rm[sid] for sid in ids]}
        check_result(mode, payload, output)
        assert sha(payload) == batch['input_sha256'], 'Batch input mismatch'
        assert sha(output) == batch['output_sha256'], 'Batch output mismatch'
    assert seen['translate'] == set(inputs), 'Missing translation provenance'
    assert seen['review'] == set(rm), 'Missing review provenance'
    assert read(run / 'human-review-queue.jsonl') == build_queue(sources, translations, reviews), 'Queue mismatch'
    print(f'PASS: {len(translations)} translations, {len(reviews)} reviews; provenance and review queue verified')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('run_dir', type=Path, nargs='?', default=ROOT / 'results')
    parser.add_argument('--require-review', action='store_true')
    args = parser.parse_args()
    validate_run(args.run_dir, args.require_review)
