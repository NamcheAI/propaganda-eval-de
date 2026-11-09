"""Independently recalculate published tables from the downloadable case/status records."""
import argparse
from collections import Counter
import json
from pathlib import Path


def verify(directory):
    d = json.loads((directory/'comparison.json').read_text())
    cases = [json.loads(line) for line in (directory/'cases.jsonl').read_text().splitlines()]
    statuses = [json.loads(line) for line in (directory/'status.jsonl').read_text().splitlines()]
    key = lambda row: (row['model'], row['language'], row['id'])
    records = {key(row): row for row in cases}
    assert len(records) == len(cases)
    assert len(statuses) == len(d['models']) * 2 * 803
    assert len({key(row) for row in statuses}) == len(statuses)
    for row in statuses:
        assert row['included'] == (key(row) in records)
    model_ids = {m['name']: m['model'] for m in d['models']}

    def aggregate(model, ids):
        result = {'n': len(ids)}
        for lang in ('en', 'de'):
            rows = [records[model_ids[model], lang, sid] for sid in ids]
            assert all(type(r['score']) is int and 0 <= r['score'] <= 5 for r in rows)
            result[lang] = {'fact_mean': sum(r['score'] for r in rows)/len(rows),
                           'propaganda_count': sum(r['propaganda'] for r in rows),
                           'refusal_count': sum(r['refused'] for r in rows)}
        return result

    pairs = {}
    for m in d['models']:
        arms = [{r['id'] for r in cases if r['model'] == m['model'] and r['language'] == lang} for lang in ('en', 'de')]
        ids = sorted(arms[0] & arms[1]); pairs[m['name']] = set(ids)
        assert ids == m['paired_ids']
        assert aggregate(m['name'], ids) == m['paired']
        assert aggregate(m['name'], d['shared_ids']) == m['shared']
        for lang in ('en', 'de'):
            rows = [r for r in statuses if r['model'] == m['model'] and r['language'] == lang]
            expected = d['diagnostics'][m['name']][lang]
            assert dict(Counter(r['answer_status'] for r in rows)) == expected['answer_status']
            assert dict(Counter(r['grade_status'] for r in rows)) == expected['grade_status']
            assert sum(r['included'] for r in rows) == expected['valid']
    assert sorted(set.intersection(*pairs.values())) == d['shared_ids']
    p = d['primary_transfer']
    assert sorted(pairs['Arete'] & pairs['Qwen']) == p['ids']
    assert p['n'] == len(p['ids'])
    for name in ('Arete', 'Qwen'):
        assert aggregate(name, p['ids']) == p['models'][name]
    for lang in ('en', 'de'):
        a, q = p['models']['Arete'][lang], p['models']['Qwen'][lang]
        assert p['gains'][lang] == {'fact_gain': a['fact_mean'] - q['fact_mean'],
            'propaganda_reduction_percentage_points': (q['propaganda_count'] - a['propaganda_count'])/p['n']*100}
    for metric in p['gains']['en']:
        assert p['difference_de_minus_en'][metric] == p['gains']['de'][metric] - p['gains']['en'][metric]
    original_ids = Counter(r['id'] for r in statuses if r['model'] in (model_ids['Arete'], model_ids['Qwen'])
                           and r['original_grade_status'] == 'ok' and r['included'])
    ids = sorted(sid for sid, count in original_ids.items() if count == 4)
    raw = p['without_validation_feedback']
    assert raw['ids'] == ids and raw['n'] == len(ids)
    for name in ('Arete', 'Qwen'):
        assert aggregate(name, ids) == raw['models'][name]
    assert sorted(sid for group in p['by_question_type'].values() for sid in group['ids']) == p['ids']
    for group in p['by_question_type'].values():
        for name in ('Arete', 'Qwen'):
            assert aggregate(name, group['ids']) == group['models'][name]
    print(f"Verified {len(cases)} valid records; {p['n']} primary and {len(d['shared_ids'])} all-model cases.")


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--directory', type=Path, default=Path(__file__).resolve().parents[1]/'eval/article-comparison')
    verify(p.parse_args().directory)
