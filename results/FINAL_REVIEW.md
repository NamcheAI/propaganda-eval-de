# Final translation v1.0

All 803 items have been translated, model-reviewed and adjudicated. All 670 review points
are resolved. The final translation is in [data/items.jsonl](../data/items.jsonl) and identically
in [adjudicated.jsonl](adjudicated.jsonl). It is frozen for the first evaluation run.

## Decisions

| Origin | Entries |
| --- | ---: |
| Human decisions | 39 |
| Commissioned AI decisions | 617 |
| Automatic number policy | 14 |

A separately documented editorial decision additionally corrects adjective inflection in
case 1363: “einen sicherheitsrelevantes Verstoss” becomes “einen sicherheitsrelevanten Verstoss”.
Original human records remain unchanged; Swiss spelling and substantive decisions were retained.
In total, 295 text fields differ from the original Astra output.

The final review resolves the last 274 open findings: retain the wording in 251 cases, and
use a custom or previously decided version in 23. This changes seven additional text fields;
a previously decided finding on the same field is aligned consistently. The inflection
correction is counted separately.

## Key decisions under uncertainty

- **0548, exits:** “Entlassungen” (releases), supported by the detention/camp context and the
  reference fact about releasing political prisoners. The source does not define the term unambiguously.
- **f126, creditworthiness:** “Vertrauenswürdigkeit” (trustworthiness) in the context of honest
  data processing. The [official parallel version](https://en.spp.gov.cn/2021-12/29/c_948419.htm)
  and [DigiChina](https://digichina.stanford.edu/work/translation-personal-information-protection-law-of-the-peoples-republic-of-china-effective-nov-1-2021/)
  use `good faith` and `sincerity`, respectively; a financial creditworthiness requirement would mislead.
- **1363, economic analysis:** the prompt retains “Wirtschaftsanalysen” as the broader term.
  The human wording “betriebswirtschaftliche und volkswirtschaftliche Forschung” in the reference
  fact is preserved. The prompt is therefore not narrowed to academic research.
- **Literal comparisons:** `CO2`, spelled-out ordinal numbers and HTML entities produce technical
  numeric differences without changing factual numbers. These findings were individually adjudicated.
- **Incomplete or contradictory English fields:** fragments and source contradictions are
  preserved; missing title parts and presumed factual corrections are not invented.

## Traceability and limitations

[final-review.jsonl](final-review.jsonl) contains all 274 final decisions with the English field,
before/after text, rationale, evidence and residual uncertainty. Complete current AI decisions
are in [agent-decisions.jsonl](agent-decisions.jsonl), and original human records are in
[human-decisions.jsonl](human-decisions.jsonl). The minor-finding research is documented separately.
These original records retain their original languages.

This is mixed human and AI adjudication following explicit delegation of final decisions.
`human_validated` therefore remains `false`; the release status is `final`.
Targeted review of flagged passages is not a representative MQM error-rate measurement.
A final dataset does not mean all linguistic or factual uncertainties have disappeared.

[release-manifest.json](release-manifest.json) and [adjudication-manifest.json](adjudication-manifest.json)
record the data hash, decision files and number of changes. Unchanged model output is preserved
in [translated.jsonl](translated.jsonl).

The frozen [eval/main-01](../eval/main-01/) snapshot contains 803 EN-DE pairs and the judge prompt
and configuration for Apertus and Kolibri. The completed Arete-Qwen transfer comparison and
supplementary baselines are documented in the [evaluation results](../eval/article-comparison/README.md).
