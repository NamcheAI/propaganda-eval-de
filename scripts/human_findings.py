"""Validate manually added findings without mixing them into model outputs."""
from datetime import datetime
import json
from common import FIELDS


def field_text(row, field, index):
    if field not in FIELDS or field not in row:
        raise ValueError('Unbekanntes Feld')
    value = row[field]
    if isinstance(value, list):
        if type(index) is not int or not 0 <= index < len(value):
            raise ValueError('Ungültiger Feldindex')
        return value[index]
    if index is not None:
        raise ValueError('Ein Textfeld hat keinen Listenindex')
    return value


def load_findings(directory, sources, translations):
    path = directory / 'human-findings.jsonl'
    findings = [json.loads(x) for x in path.read_text().splitlines() if x.strip()] if path.exists() else []
    source = {r['id']: r for r in sources}; target = {r['id']: r for r in translations}
    seen = set()
    for q in findings:
        if q['issue_id'] in seen or q.get('origin') != 'human':
            raise ValueError('Duplicate or invalid human finding')
        seen.add(q['issue_id'])
        if q['source'] != field_text(source[q['item_id']], q['field'], q['index']) or q['translation'] != field_text(target[q['item_id']], q['field'], q['index']):
            raise ValueError('Stale human finding')
        for key in ('reporter', 'reporter_role', 'reason'):
            if not isinstance(q.get(key), str) or not q[key].strip():
                raise ValueError('Missing human finding attribution or reason')
        if datetime.fromisoformat(q['created_at']).utcoffset() is None:
            raise ValueError('Human finding timestamp needs a timezone')
    return findings
