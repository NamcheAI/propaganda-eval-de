# Case-by-case review of minor findings

Minor-review status: 8 November 2026. Commissioned AI adjudication by Codex.
The final release status is documented in [FINAL_REVIEW.md](FINAL_REVIEW.md).

## Scope and results

All 344 minor findings that were open at the start were reviewed, across 286 items.
The 39 previously stored human decisions were preserved unchanged.

| Decision | Findings |
| --- | ---: |
| Model proposal accepted (`accept`) | 137 |
| Custom correction (`modify`) | 85 |
| Finding rejected, translation retained (`reject`) | 121 |
| Deferred (`defer`) | 1 |

222 decisions change the text in 221 distinct fields across 187 items.
Several findings may concern the same field. These counts are not a dataset error rate.

## Procedure

The owner commissioned a brief investigation and documented decision for each minor finding.

Each finding was checked against the English benchmark field, German translation, model
finding and available source context. The criterion is fidelity, particularly actors,
modality, quantifiers, political framing and specialist terminology. Purely stylistic variants
do not require changes. The English benchmark remains authoritative even if an underlying
article or legal text provides more detail. The approved German number policy continues to apply.

Research used linked original sources, official parallel versions, specialist sources and,
for language questions, resources such as the [Duden date rule](https://www.duden.de/sprachwissen/rechtschreibregeln/datum).
PDF text was extracted with `pdftotext` where technically possible. Search excerpts or
supplementary sources were used for blocked or unreadable sources. A successful HTTP request
alone does not count as substantive confirmation.

Extracted text from the stated source was available for 239 findings, and a relevant search
excerpt for 86. The original source was unusable for 19; supplementary evidence or a decision
limited to unambiguous EN-DE wording is documented for each. These categories describe source
access, not complete verification of every factual claim in an item.

Review took place in the interactive Codex workflow, not another standardized API review run
with a new fixed prompt. The documented Astra and Fable prompts and raw responses remain
unchanged. Methodological foundations and limitations are documented in [METHOD.md](../METHOD.md#sources).
This AI review does not replace independent, qualified human MQM assessment or a representative sample.

## Evidence and working translation

- [agent-decisions.jsonl](agent-decisions.jsonl): decision, rationale, evidence, time and AI role per issue ID.
- [agent-research.jsonl](agent-research.jsonl): English field, German wording before/after review, source access and limitations per finding.
- [agent-review-manifest.json](agent-review-manifest.json): scope and checksums of the artifacts used.
- [working-translation.jsonl](working-translation.jsonl): working translation incorporating human decisions, AI decisions and the number policy.

In the local interface, AI decisions can be inspected under “Entschieden” (decided) and
overridden by a human. Deferred findings remain open. Human decisions take precedence;
a later conflicting field decision requires renewed review of affected AI decisions.
Original decision and research records remain in their original languages.

## Final decision

**Case 0548, prompt:** “camps, exits, birth rates”. Research does not reliably establish whether
“exits” means release from camps or departure from China. The commissioned final adjudication
chooses **“Entlassungen” (releases)**, based on the detention/camp context and the reference fact
about releasing political prisoners. Residual uncertainty remains documented.
All other findings have also been decided; the final translation has no open review points.
