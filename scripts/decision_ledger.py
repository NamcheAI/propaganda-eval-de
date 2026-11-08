"""Combine separately attributed agent and human decisions without silent overrides."""
import json

from number_policy import normalize


def read_optional(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()] if path.exists() else []


def load_decisions(directory, issues):
    human = read_optional(directory / 'human-decisions.jsonl')
    agent = read_optional(directory / 'agent-decisions.jsonl')
    lookup = {q['issue_id']: q for q in issues}
    for ledger in (human, agent):
        ids = [d['issue_id'] for d in ledger]
        if len(ids) != len(set(ids)) or set(ids) - lookup.keys():
            raise ValueError('Unknown or duplicate decision')
    human_ids = {d['issue_id'] for d in human}
    human_fields = {}
    for d in human:
        q = lookup[d['issue_id']]
        location = (q['item_id'], q['field'], q['index'])
        human_fields.setdefault(location, []).append(d)
    effective = []
    for d in agent:
        if d['issue_id'] in human_ids:
            continue
        q = lookup[d['issue_id']]
        location = (q['item_id'], q['field'], q['index'])
        incompatible = any(h['decision'] == 'defer' or (
            d['decision'] != 'defer' and normalize(q['source'], h['final_text']) !=
            normalize(q['source'], d['final_text'])) for h in human_fields.get(location, []))
        if incompatible:
            # A new human field choice invalidates, rather than silently rewrites, agent approval.
            d = {**d, 'decision': 'defer', 'final_text': None,
                 'superseded_by_human_field': True,
                 'reason': 'Menschliche Entscheidung für dasselbe Feld hat Vorrang. '
                           'KI-Befund erneut prüfen. Ursprüngliche Begründung: ' + d['reason']}
        effective.append({**d, 'decision_origin': 'agent'})
    effective += [{**d, 'decision_origin': 'human'} for d in human]
    corrections = read_optional(directory / 'editorial-corrections.jsonl')
    for correction in corrections:
        for index, d in enumerate(effective):
            q = lookup[d['issue_id']]
            location = (q['item_id'], q['field'], q['index'])
            target = (correction['item_id'], correction['field'], correction['index'])
            if location == target and d.get('final_text') == correction['before']:
                effective[index] = {**d, 'decision': 'modify', 'final_text': correction['after'],
                    'decision_origin': 'agent', 'editorial_correction_id': correction['id'],
                    'previous_reviewer': d['reviewer'], 'reviewer': correction['reviewer'],
                    'reviewer_role': correction['reviewer_role'],
                    'reason': d['reason'] + ' Redaktionelle Schlusskorrektur: ' + correction['reason'],
                    'decided_at': correction['decided_at']}
    return effective
