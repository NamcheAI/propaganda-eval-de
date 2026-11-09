# Qwen: English-German run 01

803 frozen questions per language and model, one run.
Final results after targeted retries of missing or invalid calls.

| Model | Language | n | Fact score (0 to 5) | Propaganda | Refusals |
| --- | --- | ---: | ---: | ---: | ---: |
| Qwen | EN | 803 | 2.179 | 166/803 (20.672%) | 24/803 |
| Qwen | DE | 803 | 1.800 | 199/803 (24.782%) | 10/803 |

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
