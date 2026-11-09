# Qwen: EN-DE-Lauf 01

803 eingefrorene Fragen je Sprache und Modell, ein Lauf.
Finaler Stand nach gezielter Wiederholung fehlender oder ungültiger Aufrufe.

| Modell | Sprache | n | Faktenscore (0 bis 5) | Propaganda | Verweigerungen |
| --- | --- | ---: | ---: | ---: | ---: |
| Qwen | EN | 803 | 2,179 | 166/803 (20,672 %) | 24/803 |
| Qwen | DE | 803 | 1,800 | 199/803 (24,782 %) | 10/803 |

Die Tabelle verwendet nur vollständige EN-DE-Paare. Sie imputiert keine Nullwerte.
Für den direkten Modellvergleich werden die Fallmengen nochmals vereinheitlicht:
[gemeinsamer Ergebnisbericht und Grenzen](../article-comparison/README.md).

## Reproduzierbare Dateien

- [Manifest](manifest.json), `manifest.sha256`, [EN](en.jsonl), [DE](de.jsonl)
  und [englische Judge-Rubrik](judge.md): unveränderte Eingaben und Parameter.
- [Bericht](report.json): Aggregate, Ausfälle und Fragetypen.
- [Antworten](release/answers.jsonl), [ursprüngliche Urteile](release/grades.jsonl): finale
  Versuche einschließlich Fehlern, Requests, Modellantworten und Zeitstempeln.
- [Validierungskorrekturen](release/grade-repairs.jsonl) und
  [ausgewählte Bewertungen](release/selected-grades.jsonl): getrennte, an die
  Prüfsumme des ursprünglichen Urteils gebundene Korrekturen nach Fehlerrückmeldung.
- [Sprachpaare](release/pairs.jsonl): alle 803 IDs pro Modell mit Einschlussstatus.
- [Versuchsmetadaten](release/attempts.jsonl) und [Prüfsummen](release/sha256.json).

Gültige Antworten und Urteile wurden nicht ersetzt. Frühere vollständige
Versuchdateien bleiben lokal erhalten. Der Reparaturlauf änderte weder Prompt,
Rubrik noch Modellparameter. Ein Lauf liefert keine Streuung über Wiederholungen;
die sprachübergreifende Judge-Qualität wurde nicht unabhängig kalibriert.
