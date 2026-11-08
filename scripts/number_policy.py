"""Source-anchored number formatting, separate from immutable model outputs."""
from collections import Counter, defaultdict
import copy
import json
from pathlib import Path
import re

from common import FIELDS
from human_findings import field_text

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / 'policies/numbers-de.json'
NUMBER = re.compile(r'(?<!\w)\d+(?:[.,]\d+)*(?!\w)')
ENGLISH = re.compile(r'(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?\Z')
PROTECTED = re.compile(
    r'https?://[^\s<>"”]+|\b\d{1,4}[./]\d{1,2}[./]\d{2,4}\b|'
    r'\b(?:version|release|article|artikel|section|abschnitt|§)\s+\d+(?:\.\d+)+', re.I)


def tokens(text):
    protected = [m.span() for m in PROTECTED.finditer(text)]
    for match in NUMBER.finditer(text):
        if not any(a < match.end() and match.start() < b for a, b in protected):
            yield match


def normalize(source, target):
    """Accept original or already localized tokens; never guess between two values."""
    variants = defaultdict(set)
    for match in tokens(source):
        value = match.group()
        if not ENGLISH.fullmatch(value):
            continue
        german = value.translate(str.maketrans(',.', '.,'))
        variants[value].add(german)
        variants[german].add(german)
    replacements = []
    for match in tokens(target):
        choices = variants.get(match.group(), set())
        if len(choices) == 1:
            replacements.append((match.start(), match.end(), next(iter(choices))))
    for start, end, value in reversed(replacements):
        target = target[:start] + value + target[end:]
    return target


def literals_equal(source, target):
    expected = normalize(source, source)
    actual = normalize(source, target)
    patterns = (r'\d+(?:[.,]\d+)*', r'[\u3400-\u9fff]+', r'https?://[^\s<>\"]+')
    return all(Counter(re.findall(p, expected)) == Counter(re.findall(p, actual)) for p in patterns)


def covered(issue, policy):
    if issue.get('origin') not in ('reviewer', 'translator', 'literal_check', 'undocumented_change'):
        return False
    source, before = issue['source'], issue['translation']
    after = normalize(source, before)
    if issue.get('origin') == 'literal_check':
        return literals_equal(source, before)
    proposal = issue.get('suggestion') or issue.get('alternative')
    if proposal and before != proposal and normalize(source, proposal) == after:
        return True
    return (before != after and issue['issue_id'] in policy['reviewed_format_only_issue_ids'])


def working_rows(sources, translations, issues, decisions):
    rows = copy.deepcopy(translations)
    by_id = {r['id']: r for r in rows}
    source_by_id = {r['id']: r for r in sources}
    lookup = {q['issue_id']: q for q in issues}
    changes = {}
    for decision in decisions:
        if decision['decision'] == 'defer':
            continue
        q = lookup[decision['issue_id']]
        location = (q['item_id'], q['field'], q['index'])
        value = normalize(q['source'], decision['final_text'])
        if location in changes and changes[location] != value:
            raise ValueError('Conflicting decisions for one field')
        changes[location] = value
    for (sid, field, index), value in changes.items():
        if index is None:
            by_id[sid][field] = value
        else:
            by_id[sid][field][index] = value
    for row in rows:
        for field in FIELDS:
            if field not in row:
                continue
            source = source_by_id[row['id']][field]
            if isinstance(row[field], list):
                row[field] = [normalize(a, b) for a, b in zip(source, row[field])]
            else:
                row[field] = normalize(source, row[field])
    return rows


def policy_decisions(issues, decisions, rows):
    policy = json.loads(POLICY.read_text())
    existing = {d['issue_id'] for d in decisions}
    by_id = {r['id']: r for r in rows}
    result = []
    for q in issues:
        if q['issue_id'] in existing or not covered(q, policy):
            continue
        result.append({'issue_id': q['issue_id'], 'decision': 'modify',
            'reviewer': 'Projektregel ' + policy['id'], 'reviewer_role': 'Automatische Regelanwendung',
            'reason': policy['rule'], 'final_text': field_text(by_id[q['item_id']], q['field'], q['index']),
            'evidence': ['policies/numbers-de.json'], 'policy_id': policy['id'],
            'decided_at': policy['recorded_at']})
    return result
