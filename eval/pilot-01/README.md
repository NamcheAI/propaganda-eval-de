# Technical pilot

Six prespecified cases, English and German, two models: 24 responses and 24 valid judge
judgments. All twelve EN-DE pairs can be evaluated completely.

This tests the technical implementation using the draft translation. The six cases do not
support general claims about language differences or model rankings. Human comparison
against the judge's judgments remains outstanding.

`manifest.json` records selection, settings and input checksums. `answers.jsonl` and
`grades.jsonl` contain results; `report.json` contains the paired analysis.
Unchanged input and judge-prompt snapshots are included. Transport requests and technical
intermediate files remain in the local run cache.
