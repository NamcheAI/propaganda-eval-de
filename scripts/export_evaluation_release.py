"""Export reproducible final records and attempt metadata for an evaluation snapshot."""
import argparse
import hashlib
import json
from pathlib import Path

import evaluate as ev

FIELDS = ('id', 'language', 'model', 'request', 'request_sha256', 'started_at',
          'status', 'response', 'returned_model', 'finish_reason', 'usage',
          'provider_refusal', 'verdict', 'error', 'completed_at', 'routing_metadata', 'provenance')


def export(run):
    manifest = ev.load(run)
    items = {i['id']: i for i in ev.read(run / 'en.jsonl')}
    report = json.loads((run / 'report.json').read_text())['models']
    out = run / 'release'
    out.mkdir(exist_ok=True)
    records = {stage: {} for stage in ('answers', 'grades', 'grade-repairs')}
    selected_rows = []
    attempts = []
    for stage in records:
        rows = []
        for model in manifest['config']['models']:
            for sid in manifest['item_ids']:
                for lang in ('en', 'de'):
                    path = ev.path_for(run, stage, model, lang, sid)
                    if path.exists():
                        original = json.loads(path.read_text())
                        row = {k: original[k] for k in FIELDS if k in original}
                        records[stage][model, sid, lang] = row
                        rows.append(row)
                    for apath in sorted((path.parent / (sid + '-attempts')).glob('*.json'), key=lambda p: int(p.stem)):
                        attempt = json.loads(apath.read_text())
                        attempts.append({'stage': stage, 'model': model, 'id': sid, 'language': lang,
                            'attempt': int(apath.stem), 'sha256': ev.digest(apath),
                            **{k: attempt[k] for k in ('status', 'error', 'request_sha256', 'started_at', 'completed_at') if k in attempt}})
        ev.jsonl(out / (stage + '.jsonl'), rows)
    pairs = []
    for model in manifest['config']['models']:
        model_pairs = []
        for sid in manifest['item_ids']:
            pair = {'id': sid, 'model': model, 'question_description': items[sid]['question_description']}
            for lang in ('en', 'de'):
                a = records['answers'].get((model, sid, lang), {})
                selected = ev.selected_grade_path(run, model, lang, sid)
                source = 'grade-repairs' if selected == ev.path_for(run, 'grade-repairs', model, lang, sid) else 'grades'
                g = records[source].get((model, sid, lang), {})
                if g:
                    selected_rows.append({**g, 'grade_source': source})
                valid = a.get('status') == 'ok' and g.get('status') == 'ok'
                if valid:
                    ev.validate_grade(items[sid], a['response'], g['verdict'])
                pair[lang] = {'answer_status': a.get('status', 'missing'), 'grade_status': g.get('status', 'missing'),
                    'grade_source': source,
                    'score': g['verdict']['score'] if valid else None,
                    'propaganda': g['verdict']['propaganda'] if valid else None,
                    'refused': g['verdict']['refused'] if valid else None}
            pair['included'] = all(pair[l]['score'] is not None for l in ('en', 'de'))
            model_pairs.append(pair)
        selected = [p for p in model_pairs if p['included']]
        assert len(selected) == report[model]['paired_items']
        for lang in ('en', 'de'):
            expected = report[model]['paired_metrics'][lang]
            assert sum(p[lang]['score'] for p in selected) / len(selected) == expected['fact_mean']
            assert sum(p[lang]['propaganda'] > 0 for p in selected) / len(selected) == expected['any_propaganda']
        pairs.extend(model_pairs)
    ev.jsonl(out / 'pairs.jsonl', pairs)
    ev.jsonl(out / 'selected-grades.jsonl', selected_rows)
    ev.jsonl(out / 'attempts.jsonl', attempts)
    ev.write(out / 'sha256.json', {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.glob('*.jsonl'))})
    print(run, 'exported:', len(pairs), 'pairs;', sum(p['included'] for p in pairs), 'included')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', type=Path, required=True)
    export(parser.parse_args().run)
