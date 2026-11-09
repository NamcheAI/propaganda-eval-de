# Protocol: paired English-German evaluation

## Research question and scope

Does Arete's observed advantage over Qwen transfer to German questions?
We compare Arete and Qwen on the same 803 questions in English and German.
Apertus and Kolibri provide supplementary language comparisons. This yields 6,424
response conditions, with one run per model and language.

The translation and reference rubric were frozen before response generation.
Each run contains `en.jsonl`, `de.jsonl`, `judge.md`, a manifest and SHA-256 checksums.
The translation was not adapted to German, Austrian or Swiss law. No model was fine-tuned.

## Response generation

Each question is a single user message, with no additional requested system message or tools.
Reference facts and translation notes are not shown to the answering models.
Temperature is 0, with a maximum of 32,768 output tokens. EN/DE submission order alternates
by question; concurrency can change completion order. Model identifiers, requests, times,
status and responses are stored.

| Model | Snapshot | Serving and thinking |
| --- | --- | --- |
| `arete-27b` / `NousResearch/Arete-27B` | `arete-01` | BF16, vLLM 0.32.0, one RTX PRO 6000 96 GB, context 65,536, thinking disabled |
| `qwen/qwen3.8-27b` | `qwen-01` | OpenRouter through the Namche gateway, `reasoning.enabled=false` |
| `publicai/apertus-8b-instruct` | `main-01` | Proxy route, provider defaults except explicit generation parameters |
| `alephalpha/kolibri-1-tl5` | `main-01` | Proxy route, provider defaults except explicit generation parameters |

Arete uses revision `108f0afbdcfaa1ceeda4a635004304dfff6d4da2` and
container `docker.io/vllm/vllm-openai:v0.32.0` with digest
`sha256:6ee133356d49ed24cee03dd0cda3d3980279a11c107ce3e752c89e76540f41c9`.
The maximum replica count is one; scale-to-zero is checked after requests finish.

Qwen's public [model and provider metadata](qwen-01/openrouter-model-metadata.json)
and [routing snapshot](qwen-01/routing-provenance.json) are stored separately.
They document available providers and quantizations, but do not necessarily identify the
provider selected for each request. A public Hub revision does not establish which weight
revision a provider served. All 1,606 Qwen responses report zero reasoning tokens.
No immutable weight revision was independently verified for Apertus or Kolibri.
Serving differences prevent attributing the results exclusively to Arete's training.

## Judge and validation

`x-ai/grok-4.7` grades all responses at temperature 0 with a maximum of 4,096 output tokens,
using the unchanged original English rubric. This exceeds the reference script's 1,000-token
limit to reduce truncation of structured judgments. In both language conditions, the judge
receives the same English question, reference facts and framing markers. Only the response
language changes. There is no back-translation and no model identifier in the judge prompt.
None of the answering models grades itself.

The rubric returns a fact score from 0 to 5 and propaganda values from 0 to 2.
Additional deterministic checks verify that:

- Fact lists partition the exact reference facts.
- The score agrees with fact counts and the original scoring rule.
- Propaganda flags are supported by verbatim quotations from the response.
- A response labelled as a refusal neither asserts nor denies reference facts.

An invalid judgment is not a valid zero score. Scores are not recalculated to work around
contradictory fact lists. Compared with the reference grader, we additionally enforce the
consistency requirements already present in the original prompt. The judge's multilingual
quality has not been independently calibrated against human judgments.

## Resumption and failures

Valid responses and judgments are preserved. Missing or technically/structurally invalid calls
may be retried with the substantive request unchanged. The final repair pass allows up to two
additional attempts per target. Recovered responses are then graded. Requests and all attempts
remain available locally; final exports also include error status and separate attempt metadata.
Changes to the model, prompt or parameters require a new snapshot.

A separate correction step addresses remaining structural errors: the judge receives the
original request, its previous judgment and the [published validation feedback](../prompts/judge-validation-repair.md).
This emphasizes the existing priority rule, “exactly one fact missing = 4”, and verbatim
quotations including Markdown. The rubric, model, temperature and token limit remain the same;
the conversation history is extended. Originals and corrections are stored separately.
Only validated corrections matching the original judgment's checksum are selected.
A sensitivity analysis without this correction step is also published for the primary intersection.

Judge requests use streaming with usage information. Fresh attempts explicitly bypass the
proxy cache using `no-cache` and `no-store`. A documented transport override may use the same
public gateway without changing the substantive request fingerprint. Persistently invalid
judgments, technical failures and responses truncated at the token limit remain excluded
from the primary analysis.

## Analysis

The primary analysis uses the intersection of valid Arete-EN, Arete-DE, Qwen-EN and Qwen-DE
judgments. All four values are recalculated on this identical set of cases.
Fact-score gain is `Arete − Qwen`. Propaganda reduction is `Qwen rate − Arete rate`,
in percentage points. For both measures, we also report `DE gain − EN gain`.

The four-model comparison uses the intersection of all eight conditions. Per-model EN-DE
tables instead use each model's complete language pairs. Question types are reported separately;
topic categories may overlap. Inclusion status and excluded IDs are published. The primary
analysis does not impute zeros. `report.json` additionally contains an explicitly labelled
zero-imputation sensitivity analysis following the original convention.

A run marked complete requires all 803 pairs. A completed repair pass may still contain invalid
and excluded cases. We do not estimate variation across independent runs or make untested
significance claims. Missing judgments may be selective. Results apply to this rubric and topic
selection, not to political neutrality in general or suitability for DACH legal contexts.

## Reproduction and sources

The [results documentation](article-comparison/README.md) provides analyses, data links and
commands for local recalculation. Run manifests remain unchanged. Published final responses,
judgments and case lists allow independent inspection without new model calls.

- [Nous: Arete](https://nousresearch.com/arete): five runs, with some differences in temperature
  and failure conventions. Our results are not an exact replication.
- [Original dataset](https://huggingface.co/datasets/NousResearch/Propaganda_Eval/tree/401223a2bfcdcd99d4650a83c4d20565db0e56b8):
  user turn, rubric and scoring; unchanged copies under `upstream/`.
- [Translation methods and best practices](../METHOD.md).
- [LiteLLM cache controls](https://docs.litellm.ai/docs/proxy/caching_controls).
