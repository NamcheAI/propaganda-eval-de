# Methods

## Source material and translation

We translated all 803 items from the pinned revision of
[NousResearch/Propaganda_Eval](https://huggingface.co/datasets/NousResearch/Propaganda_Eval).
The translated fields are `prompt`, `required_facts`, `anchor` and, where present,
`official_frame_markers`. IDs, sources, categories, question types, list lengths
and list order are preserved.

The initial translation used `chatgpt/gpt-6-astra`, `reasoning_effort: high`, through
`https://inference.namche.net/v1/chat/completions`. Each batch contained five consecutive
items. The output limit was 24,000 tokens; temperature, top_p and seed used provider defaults.
The [translation prompt used](prompts/v1/translate.md) prioritizes fidelity, attribution,
negation, degrees of certainty, political connotations and terminology. It requests German
spelling with ß. Questions are translated, not answered; factual claims are not silently corrected.
The ChatGPT route adds the [provider system text](prompts/translate-provider.txt)
from LiteLLM 1.108.1. This is part of the effective model request.

## Model review

All 803 items were reviewed with `anthropic/claude-fable-5-1`, `reasoning_effort: medium`,
through the same gateway. The [review prompt used](prompts/v1/review.md) serves as the system
prompt. The reviewer receives the English fields, Astra translation and translation notes.
It does not see subsequent human decisions.
Subscription access was verified using Claude Code 2.1.308 through LiteLLM.
With `--bare --safe-mode`, a custom system prompt and tools disabled, the locally inspected
request also contained a billing block and the agent identity
`You are a Claude agent, built on Anthropic's Claude Agent SDK.`
That request contained no personal context or environment instructions.
Review uses this transport with a 24,000-token output limit and five items per batch.
Client model aliases are explicitly set to the Fable route. The reported model identifier
and client version are logged per batch. Additional observed system blocks are recorded
in [review-provider.txt](prompts/review-provider.txt). The version suffix in the billing
block is client-generated; the file documents a local inspection, not a capture of every
production request.

The reviewer distinguishes translation errors, defensible choices and stylistic preferences.
Severity levels are critical, major, minor or none. Every proposed change must link to a
specific finding against the original. Suggestions are stored separately, not automatically accepted.
Where quotations in findings differ from source or translation only in whitespace, they are
deterministically restored to the input text. Each batch logs the number of such restorations.
Text changes unsupported by a finding are detected through a deterministic comparison and
submitted separately for review as `undocumented_change`. The model text remains unchanged;
the pipeline does not invent a model rationale. This is a separate model review, not a blind
or human assessment.

## Human review and adjudication

### Approved number-formatting policy

The project owner explicitly approved [numbers-de-v1](policies/numbers-de.json):
English `1,234` becomes German `1.234`, `1.23` becomes `1,23`, and `1,234.56` becomes `1.234,56`.
Values and units are preserved. URLs, dates and technical identifiers are excluded.
Ambiguous mappings are not guessed.

The policy is applied deterministically using the English numbers, across translated fields
and stored field decisions. Original model responses and human decision records are unchanged.
The interface displays the derived working translation. `scripts/apply_number_policy.py`
exports it to `results/working-translation.jsonl` and records changes and input checksums
in `results/policy-application.json`. These exports are snapshots and can be regenerated
after further decisions.

Formatting-only proposals are identified using the complete field text. Existing findings
without a concrete proposal were individually checked for this scope; their IDs are recorded
in the policy file. Additional questions about meaning and explicitly deferred human decisions
remain open. Automatic resolutions are stored separately in `results/policy-decisions.jsonl`;
they are not additional independent expert judgments. All other decisions remain case-specific.

The current prompts in `prompts/translate.md` and `prompts/review.md` include the number policy
for new runs. The unchanged prompts from the completed model run are under `prompts/v1/`;
validation continues to check their original hashes. New runs validate numeric values while
allowing the approved formatting changes. Finalization applies the same policy.

### Case-by-case decisions

The review queue includes translator uncertainties, all reviewer findings, automatic flags
for changed numbers, Chinese characters or URLs, and explicitly identified specialist questions.
Each review point contains the original, translation, rationale, source URL and full item context.

The project owner or invited experts record each decision as follows:

```json
{"issue_id":"ID from the review queue","decision":"accept|reject|modify|defer","reviewer":"Name or stable identifier","reviewer_role":"Role or qualification","decided_at":"Date with time zone","reason":"Rationale based on the original","final_text":"Complete final field text or null","evidence":[]}
```

Unresolved, deferred or conflicting cases block finalization. For the remaining minor findings,
the project owner commissioned researched, case-by-case AI adjudication by Codex. These decisions
are stored separately in `results/agent-decisions.jsonl`. For each finding,
`results/agent-research.jsonl` records the original, before/after text, rationale, source access
and supporting evidence. See the [minor review report](results/AGENT_REVIEW.md).
This is commissioned AI adjudication, not independent human expert validation.
For release v1.0, the owner delegated decisions on all remaining findings, including uncertain
cases, to Codex. `results/final-review.jsonl` contains these 274 final decisions. Residual
uncertainties remain documented but no longer block finalization after an explicit final decision.
`results/editorial-corrections.jsonl` contains an exact before/after correction of adjective
inflection in case 1363. It applies only to the exact source text, is marked as an AI correction
and does not alter the original human record.
Human decisions take precedence. A later conflicting human decision on the same field reopens
affected AI findings without rewriting their original records. With mixed adjudication, the final
file is named `adjudicated.jsonl`.

Targeted review of flagged passages does not establish a representative dataset-wide error rate.
Such a claim would also require a prespecified random sample including unflagged items and
independent judgments by qualified human reviewers.

## Traceability

`results/config.json` records the configuration. `results/batches.jsonl` records model identifiers,
parameters, timestamps, token usage and hashes of the prompt, input and output per batch.
Token counts refer to accepted batch responses, not all failed attempts.
The actual prompt texts are under `prompts/`, translations and findings under `data/` and `results/`.
The prompts and original review records retain their original languages; translating this
documentation does not change the experimental inputs or evidence.
API keys and local run caches are not published.

Automatic checks cover structure, source and prompt hashes, batch assignment and review-queue
completeness. Retries occur only for technical or structural failures, using unchanged input text.
After four invalid JSON responses or structural failures, a batch is halved; prompts and item
texts stay the same. Actual grouping is recorded in the batch manifest. Model aliases and
provider defaults do not guarantee bitwise reproducibility.
The translation is frozen before EN-DE benchmarking. Release v1.0 is frozen in `data/items.jsonl`;
`results/release-manifest.json` records the data hash. `eval/main-01/` contains the frozen
EN-DE evaluation snapshot for Apertus and Kolibri.

## Sources

- [Freitag et al. (2021), Experts, Errors, and Context](https://aclanthology.org/2021.tacl-1.87/):
  explicit error analysis by qualified translators with sufficient context.
- [MQM Council, Uses of MQM](https://www.themqm.org/what-is-mqm/uses-of-mqm/):
  analytical translation evaluation and human validation of automatic assessments.
- [Gebru et al. (2021), Datasheets for Datasets](https://arxiv.org/abs/1803.09010):
  documentation of dataset provenance, creation, intended use and limitations.
- [LiteLLM 1.108.1, ChatGPT adapter](https://github.com/BerriAI/litellm/blob/v1.108.1/litellm/llms/chatgpt/common_utils.py):
  source of the additional provider system text; MIT, Copyright 2023 Berri AI.

Our error categories are MQM-inspired, not a standardized overall MQM score or certification.
Model choice and batch size are project decisions, not optima established by these sources.
