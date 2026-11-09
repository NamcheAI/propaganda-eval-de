#!/usr/bin/env python3
"""Build article tables from revalidated final grades, including paired transfer and shared eight-arm cases."""
import json
from collections import Counter
from pathlib import Path
import evaluate

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'eval/article-comparison'
RUNS = [('qwen-01', 'qwen/qwen3.8-27b', 'Qwen'),
        ('arete-01', 'arete-27b', 'Arete'),
        ('main-01', 'alephalpha/kolibri-1-tl5', 'Kolibri'),
        ('main-01', 'publicai/apertus-8b-instruct', 'Apertus')]


def main():
    models = []
    statuses = []
    reference = None
    for run, model, name in RUNS:
        directory = ROOT / 'eval' / run
        manifest = evaluate.load(directory)
        inputs = {k: manifest['input_hashes'][k] for k in ('en.jsonl', 'de.jsonl', 'judge.md')}
        assert reference is None or inputs == reference
        reference = inputs
        items = {x['id']: x for x in evaluate.read(directory / 'en.jsonl')}
        scores = {lang: {} for lang in ('en', 'de')}
        raw_scores = {lang: {} for lang in ('en', 'de')}
        for sid in manifest['item_ids']:
            for lang in scores:
                a_path = evaluate.path_for(directory, 'answers', model, lang, sid)
                raw_path = evaluate.path_for(directory, 'grades', model, lang, sid)
                g_path = evaluate.selected_grade_path(directory, model, lang, sid)
                a = json.loads(a_path.read_text()) if a_path.exists() else {}
                g = json.loads(g_path.read_text()) if g_path.exists() else {}
                raw = json.loads(raw_path.read_text()) if raw_path.exists() else {}
                valid = a.get('status') == 'ok' and g.get('status') == 'ok'
                statuses.append({'model': model, 'language': lang, 'id': sid,
                    'question_description': items[sid]['question_description'],
                    'answer_status': a.get('status', 'missing'),
                    'grade_status': g.get('status', 'missing'), 'included': valid,
                    'original_grade_status': raw.get('status', 'missing'),
                    'grade_source': 'validation_repair' if g_path != raw_path else 'original',
                    'answer_error': a.get('error'), 'grade_error': g.get('error'),
                    'answer_attempts': len(list((a_path.parent / (sid + '-attempts')).glob('*.json'))),
                    'grade_attempts': len(list((raw_path.parent / (sid + '-attempts')).glob('*.json'))),
                    'validation_repair_attempts': len(list((evaluate.path_for(directory, 'grade-repairs', model, lang, sid).parent / (sid + '-attempts')).glob('*.json')))})
                if not valid:
                    continue
                evaluate.validate_grade(items[sid], a['response'], g['verdict'])
                v = g['verdict']
                scores[lang][sid] = {'score': v['score'], 'propaganda': v['propaganda'] > 0,
                                    'refused': v['refused'], 'question_description': items[sid]['question_description']}
                if g_path == raw_path:
                    raw_scores[lang][sid] = scores[lang][sid]
        ids = sorted(set(scores['en']) & set(scores['de']))
        report = json.loads((directory / 'report.json').read_text())['models'][model]
        assert len(ids) == report['paired_items'], (name, len(ids), report['paired_items'])
        for lang in ('en', 'de'):
            expected = report['paired_metrics'][lang]
            assert sum(scores[lang][i]['score'] for i in ids) / len(ids) == expected['fact_mean']
            assert sum(scores[lang][i]['propaganda'] for i in ids) / len(ids) == expected['any_propaganda']
        models.append({'name': name, 'model': model, 'run': run, 'scores': scores,
                       'raw_scores': raw_scores, 'paired_ids': ids})
    primary_models = [m for m in models if m['name'] in ('Arete', 'Qwen')]
    primary_ids = sorted(set.intersection(*(set(m['paired_ids']) for m in primary_models)))
    shared = sorted(set.intersection(*(set(m['paired_ids']) for m in models)))
    def aggregate(m, ids):
        return {'n': len(ids), **{lang: {
            'fact_mean': sum(m['scores'][lang][i]['score'] for i in ids) / len(ids),
            'propaganda_count': sum(m['scores'][lang][i]['propaganda'] for i in ids),
            'refusal_count': sum(m['scores'][lang][i]['refused'] for i in ids),
        } for lang in ('en', 'de')}}
    primary = {m['name']: aggregate(m, primary_ids) for m in primary_models}
    gains = {lang: {
        'fact_gain': primary['Arete'][lang]['fact_mean'] - primary['Qwen'][lang]['fact_mean'],
        'propaganda_reduction_percentage_points': (primary['Qwen'][lang]['propaganda_count'] - primary['Arete'][lang]['propaganda_count']) / len(primary_ids) * 100,
    } for lang in ('en', 'de')}
    transfer = {'n': len(primary_ids), 'ids': primary_ids, 'models': primary, 'gains': gains,
                'difference_de_minus_en': {k: gains['de'][k] - gains['en'][k] for k in gains['en']}}
    transfer['excluded_ids'] = sorted(set(items) - set(primary_ids))
    raw_ids = sorted(set.intersection(*(set(m['raw_scores'][lang]) for m in primary_models for lang in ('en', 'de'))))
    raw_models = [{**m, 'scores': m['raw_scores']} for m in primary_models]
    transfer['without_validation_feedback'] = {'n': len(raw_ids), 'ids': raw_ids,
        'models': {m['name']: aggregate(m, raw_ids) for m in raw_models}}
    transfer['by_question_type'] = {}
    for label in sorted({i['question_description'] for i in items.values()}):
        ids = [sid for sid in primary_ids if items[sid]['question_description'] == label]
        transfer['by_question_type'][label] = {'ids': ids, 'models': {m['name']: aggregate(m, ids) for m in primary_models}}
    diagnostics = {m['name']: {lang: {
        'answer_status': dict(Counter(s['answer_status'] for s in statuses if s['model'] == m['model'] and s['language'] == lang)),
        'grade_status': dict(Counter(s['grade_status'] for s in statuses if s['model'] == m['model'] and s['language'] == lang)),
        'valid': sum(s['included'] for s in statuses if s['model'] == m['model'] and s['language'] == lang),
        'validated_corrections': sum(s['included'] and s['grade_source'] == 'validation_repair' for s in statuses if s['model'] == m['model'] and s['language'] == lang),
    } for lang in ('en', 'de')} for m in models}
    output = {'input_hashes': reference, 'expected_items': 803, 'shared_ids': shared, 'primary_transfer': transfer,
              'shared_excluded_ids': sorted(set(items) - set(shared)), 'diagnostics': diagnostics,
              'models': [{k: v for k, v in m.items() if k not in ('scores', 'raw_scores')} |
                         {'paired': aggregate(m, m['paired_ids']), 'shared': aggregate(m, shared)} for m in models],
              'limitations': ['One run per language; no calibrated multilingual judge.',
                             'Shared cases control item selection, not model size or serving differences.',
                             'Hosted Qwen and self-hosted Arete differ in serving; not a causal isolation of training.',
                             'Missing or invalid grades excluded; no zero imputation.']}
    OUT.mkdir(exist_ok=True)
    (OUT/'comparison.json').write_text(json.dumps(output, ensure_ascii=False, indent=2)+'\n')
    with (OUT/'cases.jsonl').open('w') as f:
        for m in models:
            for lang, scores in m['scores'].items():
                for sid, v in scores.items():
                    f.write(json.dumps({'model': m['model'], 'language': lang, 'id': sid, **v})+'\n')
    with (OUT/'status.jsonl').open('w') as f:
        for status in statuses:
            f.write(json.dumps(status, ensure_ascii=False)+'\n')
    print(json.dumps([{k: v for k, v in m.items() if k != 'paired_ids'} for m in output['models']], indent=2))

if __name__ == '__main__':
    main()
