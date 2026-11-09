---
license: mit
language:
- de
- en
pretty_name: Propaganda Eval DE
size_categories:
- n<1K
task_categories:
- question-answering
configs:
- config_name: de
  data_files:
  - split: test
    path: data/items.jsonl
  default: true
- config_name: en
  data_files:
  - split: test
    path: upstream/data/items.jsonl
---

# Propaganda Eval DE

A German translation of the 803 evaluation items in
[NousResearch/Propaganda_Eval](https://huggingface.co/datasets/NousResearch/Propaganda_Eval),
published by [Namche](https://namche.ai).

## Approach

1. Translate with **GPT-6 Astra, high**.
2. Review against the English original with **Claude Fable 5.1, medium**.
3. Incorporate human decisions and adjudicate remaining findings through commissioned, case-by-case AI review.
4. Document decisions, validate the final translation and freeze it for evaluation.

[Methods and sources](METHOD.md) · [Translation prompt](prompts/translate.md) · [Review prompt](prompts/review.md)

The exact prompts used in this run are preserved under [prompts/v1](prompts/v1).
The current prompts additionally include the approved German number-formatting policy.
Documentation is in English. German dataset text, original prompts and review records
remain in their original languages to preserve the experimental evidence.

## Translation results

All **803 items have been adjudicated and frozen for the first evaluation run**.
All 670 review points, including findings added later, have been resolved:
39 human decisions, 617 AI decisions and 14 applications of the number-formatting policy.
A separate editorial correction fixes an inflection error. This is mixed adjudication,
not complete independent human validation.
The Astra request also includes the documented
[provider system text](prompts/translate-provider.txt).

[Final review report](results/FINAL_REVIEW.md) · [Release manifest](results/release-manifest.json)

| File | Contents |
| --- | --- |
| [data/items.jsonl](data/items.jsonl) | Final German translation v1.0 |
| [upstream/data/items.jsonl](upstream/data/items.jsonl) | English original |
| [results/status.json](results/status.json) | Completion status of the original model run |
| [results/HUMAN_REVIEW.md](results/HUMAN_REVIEW.md) | Original review points with full context; current decisions are available in the interface |
| [results/reviews.jsonl](results/reviews.jsonl) | Model findings and proposed corrections |
| [results/human-decisions.jsonl](results/human-decisions.jsonl) | Human decisions |
| [results/agent-decisions.jsonl](results/agent-decisions.jsonl) | Commissioned case-by-case AI decisions, separate from human review |
| [results/agent-research.jsonl](results/agent-research.jsonl) | Research, source access and before/after text for each minor finding |
| [results/final-review.jsonl](results/final-review.jsonl) | Decisions on the remaining 274 findings |
| [results/working-translation.jsonl](results/working-translation.jsonl) | Working translation; identical to the final translation at release |
| [results/policy-application.json](results/policy-application.json) | Number policy, input checksums and changed fields in the latest export |
| [results/policy-decisions.jsonl](results/policy-decisions.jsonl) | Findings resolved by the number policy in the latest export |
| [results/batches.jsonl](results/batches.jsonl) | Models, parameters, timestamps and checksums per batch |

The translation preserves the original questions, facts and political framing. It adds no
DACH-specific cases and does not validate suitability for German, Austrian or Swiss law.
Review flags are not confirmed errors; unflagged items may also contain errors.
The unchanged model output is preserved in `results/translated.jsonl`.
The final translation is in `data/items.jsonl` and `results/adjudicated.jsonl`.
The EN-DE snapshot under `eval/arete-01/` contains all 803 pairs and the adjudication manifest.

## Expert interface and evaluation

The [local expert review interface](review-ui/README.md) shows originals, translations,
suggestions and documented decisions: `python3 scripts/review_ui.py`.
Its labels and the original [review dossier](results/HUMAN_REVIEW.md) are in German.

<!-- evaluation-summary:start -->
The [four-model English-German comparison](eval/article-comparison/README.md) is complete.
All 803 questions were posed to each model in both languages. On the **803 identical
Arete-Qwen cases**, Arete achieves a **0.747-point higher fact score**
and **23.661 percentage points fewer propaganda flags**
than Qwen in German. This is a descriptive finding from the first run; serving differences
limit attribution to training. We did not fine-tune a model.

The full comparison with Apertus and Kolibri uses **802 identical questions**
across all eight conditions. Invalid judgments and truncated responses remain excluded.
Data, exact case sets and limitations are documented in the
[results report](eval/article-comparison/README.md) and
[comparison data](eval/article-comparison/comparison.json).
<!-- evaluation-summary:end -->

The [evaluation protocol](eval/PROTOCOL.md) documents the runner and procedure. The earlier
[technical pilot](eval/pilot-01/README.md) tested the implementation.

## Running the pipeline

Python 3.12 or later. For translation, create a `.env` file with `INFERENCE_API_KEY`
for `https://inference.namche.net`.
The Fable route supports the configured subscription/setup token through Claude Code.
Run `python3 scripts/check_subscription.py` for a minimal test (Claude Code 2.1.308).
The test uses the gateway key from `.env`; no separate Anthropic API key is required.
Review uses the same transport with `--bare --safe-mode` and tools disabled.

```sh
python3 scripts/run.py --translate-only
python3 scripts/run.py
python3 scripts/validate.py
python3 scripts/finalize.py results
```

Existing results are reused. Finalization requires a complete model review and
documented decisions on all outstanding review points.

## Provenance and license

Original revision: `401223a2bfcdcd99d4650a83c4d20565db0e56b8`. Original and translation: MIT.
This is an independent derivative, unaffiliated with Nous Research. A first paired
Arete-Qwen language comparison and Apertus/Kolibri baselines are available.
