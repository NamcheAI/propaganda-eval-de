#!/usr/bin/env python3
"""Export the current working translation and auditable number-rule applications."""
import argparse
import hashlib
import json
from pathlib import Path

from common import FIELDS
from human_findings import field_text, load_findings
from number_policy import ROOT, POLICY, normalize, working_rows, policy_decisions
from run import jsonl, write
from decision_ledger import load_decisions, read_optional


def read(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def export_working(directory):
    sources = read(ROOT / 'upstream/data/items.jsonl')
    translations = read(directory / 'translated.jsonl')
    issues = read(directory / 'human-review-queue.jsonl') + load_findings(directory, sources, translations)
    decisions = load_decisions(directory, issues)
    rows = working_rows(sources, translations, issues, decisions)
    automatic = policy_decisions(issues, decisions, rows)
    by_id = {r['id']: r for r in rows}
    source_by_id = {r['id']: r for r in sources}
    lookup = {q['issue_id']: q for q in issues}
    human_fields = {}
    for d in decisions:
        if d['decision'] != 'defer':
            q = lookup[d['issue_id']]
            human_fields[(q['item_id'], q['field'], q['index'])] = d['final_text']
    changes = []
    for row in translations:
        for field in FIELDS:
            value = row.get(field, [])
            for index, before in (enumerate(value) if isinstance(value, list) else [(None, value)]):
                location = (row['id'], field, index)
                before = human_fields.get(location, before)
                source = field_text(source_by_id[row['id']], field, index)
                after = field_text(by_id[row['id']], field, index)
                if before != after:
                    assert normalize(source, before) == after
                    changes.append(dict(item_id=row['id'], field=field, index=index,
                                        source=source, before=before, after=after))
    resolved = {d['issue_id'] for d in decisions + automatic if d['decision'] != 'defer'}
    manifest = {'policy_id': 'numbers-de-v1', 'human_validated': False,
        'human_decisions': len(read_optional(directory / 'human-decisions.jsonl')),
        'agent_decisions': len(read_optional(directory / 'agent-decisions.jsonl')),
        'automatically_resolved_issues': len(automatic),
        'remaining_issues': len(issues) - len(resolved),
        'formatted_fields': len(changes), 'formatted_items': len({c['item_id'] for c in changes}),
        'input_sha256': {name: hashlib.sha256((directory / name).read_bytes()).hexdigest()
            for name in ('translated.jsonl', 'human-review-queue.jsonl', 'human-decisions.jsonl', 'human-findings.jsonl', 'agent-decisions.jsonl', 'editorial-corrections.jsonl')
            if (directory / name).exists()},
        'policy_sha256': hashlib.sha256(POLICY.read_bytes()).hexdigest(),
        'changes': changes}
    jsonl(directory / 'working-translation.jsonl', rows)
    jsonl(directory / 'policy-decisions.jsonl', automatic)
    manifest['output_sha256'] = hashlib.sha256((directory / 'working-translation.jsonl').read_bytes()).hexdigest()
    write(directory / 'policy-application.json', manifest)
    return {k: v for k, v in manifest.items() if k not in ('changes', 'input_sha256', 'output_sha256', 'policy_sha256')}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', type=Path, nargs='?', default=ROOT / 'results')
    print(json.dumps(export_working(parser.parse_args().directory), ensure_ascii=False))
