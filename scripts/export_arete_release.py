#!/usr/bin/env python3
"""Export final attempt records and paired inclusion decisions for Arete run 01."""
import hashlib
import json
from pathlib import Path
import evaluate

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'eval/arete-01'
OUT = RUN / 'release'
FIELDS = ('id', 'language', 'model', 'request', 'request_sha256', 'started_at',
          'status', 'response', 'returned_model', 'finish_reason', 'usage',
          'provider_refusal', 'verdict', 'error', 'completed_at')


def dump(name, rows):
    (OUT / name).write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows))


def main():
    manifest = evaluate.load(RUN)
    model, = manifest['config']['models']
    items = {i['id']: i for i in evaluate.read(RUN / 'en.jsonl')}
    records = {stage: {} for stage in ('answers', 'grades')}
    OUT.mkdir(exist_ok=True)
    for stage in records:
        rows = []
        for sid in manifest['item_ids']:
            for lang in ('en', 'de'):
                path = evaluate.path_for(RUN, stage, model, lang, sid)
                if path.exists():
                    original = json.loads(path.read_text())
                    row = {k: original[k] for k in FIELDS if k in original}
                    records[stage][sid, lang] = row
                    rows.append(row)
        dump(stage + '.jsonl', rows)
    pairs = []
    for sid in manifest['item_ids']:
        pair = {'id': sid, 'question_description': items[sid]['question_description']}
        for lang in ('en', 'de'):
            a = records['answers'].get((sid, lang), {})
            g = records['grades'].get((sid, lang), {})
            valid = a.get('status') == 'ok' and g.get('status') == 'ok'
            if valid:
                evaluate.validate_grade(items[sid], a['response'], g['verdict'])
            pair[lang] = {'answer_status': a.get('status', 'missing'),
                          'grade_status': g.get('status', 'missing'),
                          'score': g['verdict']['score'] if valid else None,
                          'propaganda': g['verdict']['propaganda'] if valid else None}
        pair['included'] = all(pair[l]['score'] is not None for l in ('en', 'de'))
        pairs.append(pair)
    dump('pairs.jsonl', pairs)
    selected = [p for p in pairs if p['included']]
    report = json.loads((RUN / 'report.json').read_text())['models'][model]
    assert len(selected) == report['paired_items'] == 775
    for lang in ('en', 'de'):
        metrics = report['paired_metrics'][lang]
        assert sum(p[lang]['score'] for p in selected)/len(selected) == metrics['fact_mean']
        assert sum(p[lang]['propaganda'] > 0 for p in selected)/len(selected) == metrics['any_propaganda']
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.glob('*.jsonl'))}
    (OUT / 'sha256.json').write_text(json.dumps(hashes, indent=2) + '\n')
    print(f'Exported {len(pairs)} cases; {len(selected)} complete pairs; aggregates verified.')


if __name__ == '__main__':
    main()
