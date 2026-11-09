# Arete, Qwen, Kolibri and Apertus: English-German comparison

803 frozen questions per model and language, one run, with results after targeted
retries of missing or technically/structurally invalid calls. All numbers follow
the original scoring rubric. The fact score is not a general truth rate;
propaganda refers to the rubric's specific markers.

## Primary question: Arete's advantage over Qwen in both languages

**803 identical questions** with valid judgments in all four conditions.
0 questions remain excluded. All four rows use the same set of cases.

| Model | Language | n | Fact score (0 to 5) | Propaganda | Refusals |
| --- | --- | ---: | ---: | ---: | ---: |
| Qwen | EN | 803 | 2.179 | 166/803 (20.672%) | 24/803 |
| Qwen | DE | 803 | 1.800 | 199/803 (24.782%) | 10/803 |
| Arete | EN | 803 | 2.917 | 7/803 (0.872%) | 1/803 |
| Arete | DE | 803 | 2.547 | 9/803 (1.121%) | 1/803 |

| Arete's advantage over Qwen | English | German | German minus English |
| --- | ---: | ---: | ---: |
| Higher fact score | 0.737 | 0.747 | 0.010 |
| Reduction in propaganda rate, percentage points | 19.801 | 23.661 | 3.861 |

Arete also shows a higher fact score and fewer propaganda flags than Qwen in German.
Both models have lower fact scores in German. This describes this run without
establishing significance or causality: hosting and quantization are not fully matched.

Without additional validation feedback, the primary intersection contains 781
questions. This sensitivity analysis and all its individual values are recorded
under `primary_transfer.without_validation_feedback` in `comparison.json`.

### Fact scores by question type, same four conditions

| Question type | Shared questions | Qwen EN | Qwen DE | Arete EN | Arete DE |
| --- | ---: | ---: | ---: | ---: | ---: |
| closed exit | 17 | 1.765 | 1.588 | 3.471 | 2.353 |
| frame testing | 222 | 3.005 | 3.014 | 3.968 | 3.860 |
| named fact | 564 | 1.867 | 1.328 | 2.486 | 2.035 |

## All four models on the same questions

**802 shared questions** across all eight conditions;
1 questions excluded. This set differs from the primary
Arete-Qwen analysis.

| Model | Language | n | Fact score (0 to 5) | Propaganda | Refusals |
| --- | --- | ---: | ---: | ---: | ---: |
| Qwen | EN | 802 | 2.177 | 166/802 (20.698%) | 24/802 |
| Qwen | DE | 802 | 1.802 | 199/802 (24.813%) | 10/802 |
| Arete | EN | 802 | 2.920 | 7/802 (0.873%) | 1/802 |
| Arete | DE | 802 | 2.550 | 9/802 (1.122%) | 1/802 |
| Kolibri | EN | 802 | 1.491 | 4/802 (0.499%) | 184/802 |
| Kolibri | DE | 802 | 1.380 | 5/802 (0.623%) | 226/802 |
| Apertus | EN | 802 | 1.618 | 19/802 (2.369%) | 24/802 |
| Apertus | DE | 802 | 1.512 | 11/802 (1.372%) | 5/802 |

## Complete language pairs for each model

These figures use different sets of cases and are not intended as a direct ranking.
Refusals are automatic judge labels.

| Model | Language | n | Fact score (0 to 5) | Propaganda | Refusals |
| --- | --- | ---: | ---: | ---: | ---: |
| Qwen | EN | 803 | 2.179 | 166/803 (20.672%) | 24/803 |
| Qwen | DE | 803 | 1.800 | 199/803 (24.782%) | 10/803 |
| Arete | EN | 803 | 2.917 | 7/803 (0.872%) | 1/803 |
| Arete | DE | 803 | 2.547 | 9/803 (1.121%) | 1/803 |
| Kolibri | EN | 803 | 1.489 | 4/803 (0.498%) | 184/803 |
| Kolibri | DE | 803 | 1.379 | 5/803 (0.623%) | 226/803 |
| Apertus | EN | 802 | 1.618 | 19/802 (2.369%) | 24/802 |
| Apertus | DE | 802 | 1.512 | 11/802 (1.372%) | 5/802 |

## Failures and retries

| Model | Language | Valid judgments | Invalid judgment | Missing judgment | Truncated response |
| --- | --- | ---: | ---: | ---: | ---: |
| Qwen | EN | 803 | 0 | 0 | 0 |
| Qwen | DE | 803 | 0 | 0 | 0 |
| Arete | EN | 803 | 0 | 0 | 0 |
| Arete | DE | 803 | 0 | 0 | 0 |
| Kolibri | EN | 803 | 0 | 0 | 0 |
| Kolibri | DE | 803 | 0 | 0 | 0 |
| Apertus | EN | 803 | 0 | 0 | 0 |
| Apertus | DE | 802 | 0 | 0 | 1 |

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
