"""Write English result documentation from the validated comparison export."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'eval/article-comparison'


def num(value):
    return f'{value:.3f}'


def table(models):
    lines = ['| Model | Language | n | Fact score (0 to 5) | Propaganda | Refusals |',
             '| --- | --- | ---: | ---: | ---: | ---: |']
    for name, values in models.items():
        for lang in ('en', 'de'):
            a, n = values[lang], values['n']
            lines.append(f"| {name} | {lang.upper()} | {n} | {num(a['fact_mean'])} | {a['propaganda_count']}/{n} ({num(a['propaganda_count']/n*100)}%) | {a['refusal_count']}/{n} |")
    return '\n'.join(lines)


def main():
    d = json.loads((OUT / 'comparison.json').read_text())
    p = d['primary_transfer']
    individual = {m['name']: m['paired'] for m in d['models']}
    shared = {m['name']: m['shared'] for m in d['models']}
    gains = p['gains']
    groups = ['| Question type | Shared questions | Qwen EN | Qwen DE | Arete EN | Arete DE |',
              '| --- | ---: | ---: | ---: | ---: | ---: |']
    for label, group in p['by_question_type'].items():
        models = group['models']
        groups.append(f"| {label} | {len(group['ids'])} | " + ' | '.join(num(models[m][lang]['fact_mean']) for m in ('Qwen', 'Arete') for lang in ('en', 'de')) + ' |')
    status = [json.loads(line) for line in (OUT/'status.jsonl').read_text().splitlines()]
    raw = p['without_validation_feedback']
    failed = ['| Model | Language | Valid judgments | Invalid judgment | Missing judgment | Truncated response |',
              '| --- | --- | ---: | ---: | ---: | ---: |']
    for m in d['models']:
        for lang in ('en', 'de'):
            rows = [r for r in status if r['model'] == m['model'] and r['language'] == lang]
            failed.append(f"| {m['name']} | {lang.upper()} | {sum(r['included'] for r in rows)} | {sum(r['grade_status'] == 'technical_error' for r in rows)} | {sum(r['grade_status'] == 'missing' and r['answer_status'] == 'ok' for r in rows)} | {sum(r['answer_status'] == 'truncated' for r in rows)} |")
    text = f'''# Arete, Qwen, Kolibri and Apertus: English-German comparison

803 frozen questions per model and language, one run, with results after targeted
retries of missing or technically/structurally invalid calls. All numbers follow
the original scoring rubric. The fact score is not a general truth rate;
propaganda refers to the rubric's specific markers.

## Primary question: Arete's advantage over Qwen in both languages

**{p['n']} identical questions** with valid judgments in all four conditions.
{803-p['n']} questions remain excluded. All four rows use the same set of cases.

{table(p['models'])}

| Arete's advantage over Qwen | English | German | German minus English |
| --- | ---: | ---: | ---: |
| Higher fact score | {num(gains['en']['fact_gain'])} | {num(gains['de']['fact_gain'])} | {num(p['difference_de_minus_en']['fact_gain'])} |
| Reduction in propaganda rate, percentage points | {num(gains['en']['propaganda_reduction_percentage_points'])} | {num(gains['de']['propaganda_reduction_percentage_points'])} | {num(p['difference_de_minus_en']['propaganda_reduction_percentage_points'])} |

Arete also shows a higher fact score and fewer propaganda flags than Qwen in German.
Both models have lower fact scores in German. This describes this run without
establishing significance or causality: hosting and quantization are not fully matched.

Without additional validation feedback, the primary intersection contains {raw['n']}
questions. This sensitivity analysis and all its individual values are recorded
under `primary_transfer.without_validation_feedback` in `comparison.json`.

### Fact scores by question type, same four conditions

{chr(10).join(groups)}

## All four models on the same questions

**{len(d['shared_ids'])} shared questions** across all eight conditions;
{len(d['shared_excluded_ids'])} questions excluded. This set differs from the primary
Arete-Qwen analysis.

{table(shared)}

## Complete language pairs for each model

These figures use different sets of cases and are not intended as a direct ranking.
Refusals are automatic judge labels.

{table(individual)}

## Failures and retries

{chr(10).join(failed)}

Successful responses and valid judgments were not replaced. The final repair pass
allowed up to two additional attempts per target with the substantive request unchanged.
For the nine recovered Arete responses, only the missing judgments were then added.
The public gateway transport did not change the rubric or model parameters.
For remaining structural errors, the same judge received its previous judgment and
[standardized validation feedback](../../prompts/judge-validation-repair.md).
This clarifies the priority of the unchanged scoring rules and verbatim copying,
including Markdown. Settings and rubric remain the same; the additional conversation
history is a documented protocol step. Only strictly validated corrections are accepted.
Original judgments are not replaced; corrections are bound to the original file's checksum.
Structurally invalid judgments were not arithmetically corrected. Generations truncated
at the token limit were also specifically retried with the same limit. Remaining invalid
or incomplete results stay excluded. Earlier technical attempts are not independent
experimental repetitions.

## Methods and limitations

- The same EN/DE files and English rubric in all three run snapshots, verified by SHA-256.
  One user message, temperature 0, maximum 32,768 output tokens.
- Arete: BF16, vLLM 0.32.0, RTX PRO 6000 96 GB, context 65,536,
  weight revision `108f0afbdcfaa1ceeda4a635004304dfff6d4da2`, thinking disabled.
- Qwen3.8-27B: OpenRouter through the Namche gateway, `reasoning.enabled=false`.
  All 1,606 responses report zero reasoning tokens. Public provider metadata documents
  available endpoints; it does not establish the specific provider or quantization used
  for every request. This is not a replication of Arete's BF16 serving configuration.
- Apertus/Kolibri: proxy routes without independently verified immutable weight revisions
  in the snapshot. Model sizes and serving configurations differ.
- Judge: Grok 4.7, original English question/facts/markers, response in EN or DE,
  temperature 0 and maximum 4,096 output tokens. Verbatim evidence, fact partitioning
  and score consistency are additionally checked deterministically.
- One run, no estimate of between-run variation; no independently calibrated multilingual
  judge. Selective failures and translation errors remain possible sources of bias.
  No DACH-specific adaptation or fine-tuning.
- Nous reports English results over five runs: Arete 2.98/0.9% and Qwen 2.32/22%.
  Different case sets, repetition counts and protocol deviations prevent a claim of
  exact replication. Our primary analysis does not impute zeros.

## Data and reproduction

- [Comparison](comparison.json): exact case sets, aggregates, transfer differences,
  question types and diagnostics.
- [Valid individual cases](cases.jsonl): all valid individual judgments, including
  those outside the paired intersections.
- [All statuses](status.jsonl): 6,424 conditions with inclusion status, exclusion
  reasons and counts of stored attempts.
- Run snapshots and final responses/judgments: [Arete](../arete-01/),
  [Qwen](../qwen-01/), [Apertus/Kolibri](../main-01/), each under `release/`.
  `release/attempts.jsonl` contains status, times, request hashes and file checksums
  for stored attempts. Complete local attempt files remain available.
  `release/grades.jsonl` stores original judgments, `grade-repairs.jsonl` separate
  corrections and `selected-grades.jsonl` the selected judgments.
- [Translation methods and sources](../../METHOD.md),
  [Nous Arete](https://nousresearch.com/arete),
  [OpenRouter model metadata](../qwen-01/openrouter-model-metadata.json).

```sh
python3 scripts/evaluate.py report --run eval/arete-01
python3 scripts/evaluate.py report --run eval/qwen-01
python3 scripts/evaluate.py report --run eval/main-01
python3 scripts/export_evaluation_release.py --run eval/arete-01
python3 scripts/export_evaluation_release.py --run eval/qwen-01
python3 scripts/export_evaluation_release.py --run eval/main-01
python3 scripts/export_article_comparison.py
python3 scripts/write_comparison_report.py
python3 scripts/update_article_results.py --site /path/to/namche.ai
```

These export commands use the run's local original files. The published `release/`
exports and `cases.jsonl` allow independent recalculation of the tables without
new model calls. Translation release v1.0.0 and its results at the time remain
unchanged under the existing tag.
'''
    (OUT/'README.md').write_text(text)
    readme = ROOT/'README.md'
    s = readme.read_text()
    start = '<!-- evaluation-summary:start -->'
    end = '<!-- evaluation-summary:end -->'
    a = s.index(start) + len(start)
    b = s.index(end, a)
    summary = f'''
The [four-model English-German comparison](eval/article-comparison/README.md) is complete.
All 803 questions were posed to each model in both languages. On the **{p['n']} identical
Arete-Qwen cases**, Arete achieves a **{num(gains['de']['fact_gain'])}-point higher fact score**
and **{num(gains['de']['propaganda_reduction_percentage_points'])} percentage points fewer propaganda flags**
than Qwen in German. This is a descriptive finding from the first run; serving differences
limit attribution to training. We did not fine-tune a model.

The full comparison with Apertus and Kolibri uses **{len(d['shared_ids'])} identical questions**
across all eight conditions. Invalid judgments and truncated responses remain excluded.
Data, exact case sets and limitations are documented in the
[results report](eval/article-comparison/README.md) and
[comparison data](eval/article-comparison/comparison.json).
'''
    readme.write_text(s[:a] + summary + s[b:])
    for run, names in [('arete-01', ['Arete']), ('qwen-01', ['Qwen']), ('main-01', ['Apertus', 'Kolibri'])]:
        models = {name: individual[name] for name in names}
        (ROOT/'eval'/run/'README.md').write_text(f'''# {', '.join(names)}: English-German run 01

803 frozen questions per language and model, one run.
Final results after targeted retries of missing or invalid calls.

{table(models)}

The table includes only complete EN-DE pairs and does not impute zeros.
For direct model comparisons, the case sets are aligned again:
[shared results report and limitations](../article-comparison/README.md).

## Reproducible files

- [Manifest](manifest.json), `manifest.sha256`, [EN](en.jsonl), [DE](de.jsonl)
  and [English judge rubric](judge.md): unchanged inputs and parameters.
- [Report](report.json): aggregates, failures and question types.
- [Responses](release/answers.jsonl), [original judgments](release/grades.jsonl): final
  attempts including errors, requests, model responses and timestamps.
- [Validation corrections](release/grade-repairs.jsonl) and
  [selected judgments](release/selected-grades.jsonl): separate corrections following
  validation feedback, bound to the original judgment's checksum.
- [Language pairs](release/pairs.jsonl): all 803 IDs per model with inclusion status.
- [Attempt metadata](release/attempts.jsonl) and [checksums](release/sha256.json).

Valid responses and judgments were not replaced. Earlier complete attempt files remain
available locally. The repair pass changed neither prompt, rubric nor model parameters.
A single run does not estimate variation across repetitions; the judge's cross-language
quality has not been independently calibrated.
''')
    print('Updated English comparison report and run documentation.')


if __name__ == '__main__':
    main()
