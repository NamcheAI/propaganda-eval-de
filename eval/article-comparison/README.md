# Arete, Qwen, Kolibri und Apertus: EN-DE-Vergleich

803 eingefrorene Fragen pro Modell und Sprache, ein Lauf, Ergebnisstand nach
gezielter Wiederholung fehlender oder technisch/formal ungültiger Aufrufe.
Alle Zahlen folgen der ursprünglichen Bewertungsrubrik. Der Faktenscore ist
keine allgemeine Wahrheitsquote; Propaganda bezeichnet deren konkrete Marker.

## Primärfrage: Aretes Vorteil gegenüber Qwen in beiden Sprachen

**803 identische Fragen** mit gültigen Bewertungen in allen vier Bedingungen.
0 Fragen bleiben ausgeschlossen. Die Fallmenge ist für alle vier Zeilen identisch.

| Modell | Sprache | n | Faktenscore (0 bis 5) | Propaganda | Verweigerungen |
| --- | --- | ---: | ---: | ---: | ---: |
| Qwen | EN | 803 | 2,179 | 166/803 (20,672 %) | 24/803 |
| Qwen | DE | 803 | 1,800 | 199/803 (24,782 %) | 10/803 |
| Arete | EN | 803 | 2,917 | 7/803 (0,872 %) | 1/803 |
| Arete | DE | 803 | 2,547 | 9/803 (1,121 %) | 1/803 |

| Vorteil Aretes gegenüber Qwen | Englisch | Deutsch | Deutsch minus Englisch |
| --- | ---: | ---: | ---: |
| Höherer Faktenscore | 0,737 | 0,747 | 0,010 |
| Verringerung des Propaganda-Anteils, Prozentpunkte | 19,801 | 23,661 | 3,861 |

Arete zeigt auch auf Deutsch einen höheren Faktenscore und weniger
Propaganda-Markierungen als Qwen. Der deutsche Faktenscore liegt bei beiden
Modellen niedriger. Das beschreibt diesen Lauf, ohne Signifikanz- oder
Kausalnachweis: Hosting und Quantisierung sind nicht vollständig angeglichen.

Ohne zusätzliche Validierungsrückmeldung umfasst die primäre Schnittmenge
781 Fragen. Diese Sensitivitätsauswertung steht mit allen Einzelwerten
unter `primary_transfer.without_validation_feedback` in `comparison.json`.

### Faktenscores nach Fragetyp, gleiche vier Bedingungen

| Fragetyp | Gemeinsame Fragen | Qwen EN | Qwen DE | Arete EN | Arete DE |
| --- | ---: | ---: | ---: | ---: | ---: |
| closed exit | 17 | 1,765 | 1,588 | 3,471 | 2,353 |
| frame testing | 222 | 3,005 | 3,014 | 3,968 | 3,860 |
| named fact | 564 | 1,867 | 1,328 | 2,486 | 2,035 |

## Alle vier Modelle auf denselben Fragen

**802 gemeinsame Fragen** in allen acht Bedingungen;
1 Fragen ausgeschlossen. Diese Fallmenge unterscheidet
sich von der primären Arete-Qwen-Auswertung.

| Modell | Sprache | n | Faktenscore (0 bis 5) | Propaganda | Verweigerungen |
| --- | --- | ---: | ---: | ---: | ---: |
| Qwen | EN | 802 | 2,177 | 166/802 (20,698 %) | 24/802 |
| Qwen | DE | 802 | 1,802 | 199/802 (24,813 %) | 10/802 |
| Arete | EN | 802 | 2,920 | 7/802 (0,873 %) | 1/802 |
| Arete | DE | 802 | 2,550 | 9/802 (1,122 %) | 1/802 |
| Kolibri | EN | 802 | 1,491 | 4/802 (0,499 %) | 184/802 |
| Kolibri | DE | 802 | 1,380 | 5/802 (0,623 %) | 226/802 |
| Apertus | EN | 802 | 1,618 | 19/802 (2,369 %) | 24/802 |
| Apertus | DE | 802 | 1,512 | 11/802 (1,372 %) | 5/802 |

## Jeweils vollständige Sprachpaare pro Modell

Diese Zahlen verwenden unterschiedliche Fallmengen und sind nicht für eine
direkte Rangliste gedacht. Verweigerungen sind automatische Judge-Labels.

| Modell | Sprache | n | Faktenscore (0 bis 5) | Propaganda | Verweigerungen |
| --- | --- | ---: | ---: | ---: | ---: |
| Qwen | EN | 803 | 2,179 | 166/803 (20,672 %) | 24/803 |
| Qwen | DE | 803 | 1,800 | 199/803 (24,782 %) | 10/803 |
| Arete | EN | 803 | 2,917 | 7/803 (0,872 %) | 1/803 |
| Arete | DE | 803 | 2,547 | 9/803 (1,121 %) | 1/803 |
| Kolibri | EN | 803 | 1,489 | 4/803 (0,498 %) | 184/803 |
| Kolibri | DE | 803 | 1,379 | 5/803 (0,623 %) | 226/803 |
| Apertus | EN | 802 | 1,618 | 19/802 (2,369 %) | 24/802 |
| Apertus | DE | 802 | 1,512 | 11/802 (1,372 %) | 5/802 |

## Ausfälle und Wiederholungen

| Modell | Sprache | Gültig bewertet | Ungültiges Urteil | Fehlendes Urteil | Abgeschnittene Antwort |
| --- | --- | ---: | ---: | ---: | ---: |
| Qwen | EN | 803 | 0 | 0 | 0 |
| Qwen | DE | 803 | 0 | 0 | 0 |
| Arete | EN | 803 | 0 | 0 | 0 |
| Arete | DE | 803 | 0 | 0 | 0 |
| Kolibri | EN | 803 | 0 | 0 | 0 |
| Kolibri | DE | 803 | 0 | 0 | 0 |
| Apertus | EN | 803 | 0 | 0 | 0 |
| Apertus | DE | 802 | 0 | 0 | 1 |

Erfolgreiche Antworten und gültige Bewertungen wurden nicht ersetzt.
Der abschließende Reparaturlauf erlaubte je Ziel bis zu zwei zusätzliche
Versuche mit unverändertem fachlichem Request. Für die neun nachgeholten
Arete-Antworten wurden anschließend nur die fehlenden Bewertungen ergänzt.
Der öffentliche Gateway-Transport änderte keine Rubrik oder Modellparameter.
Bei verbliebenen formalen Fehlern bekam derselbe Judge das vorherige Urteil und
eine [standardisierte Validierungsrückmeldung](../../prompts/judge-validation-repair.md).
Sie verdeutlicht die Priorität der unveränderten Score-Regeln und das wörtliche
Kopieren einschließlich Markdown. Einstellungen und Rubrik bleiben gleich;
der zusätzliche Gesprächsverlauf ist ein dokumentierter Protokollschritt.
Nur streng validierte Korrekturen werden übernommen. Ursprüngliche Urteile
werden nicht ersetzt; Korrekturen sind an ihre Datei-Prüfsumme gebunden.
Formal ungültige Urteile wurden nicht rechnerisch korrigiert. Auch am Tokenlimit
abgebrochene Generierungen wurden gezielt mit demselben Limit wiederholt.
Verbleibende ungültige oder unvollständige Ergebnisse bleiben ausgeschlossen.
Frühere technische Versuche sind keine unabhängigen Experimentwiederholungen.

## Methode und Grenzen

- Dieselben EN/DE-Dateien und dieselbe englische Rubrik in allen drei Run-Snapshots,
  per SHA-256 geprüft. Eine Nutzernachricht, Temperatur 0, maximal 32.768 Ausgabetoken.
- Arete: BF16, vLLM 0.32.0, RTX PRO 6000 96 GB, Kontext 65.536,
  Gewichtsrevision `108f0afbdcfaa1ceeda4a635004304dfff6d4da2`, Thinking aus.
- Qwen3.8-27B: OpenRouter über Namche-Gateway, `reasoning.enabled=false`.
  Alle 1.606 Antworten melden null Reasoning-Tokens. Öffentliche Anbieter-Metadaten
  dokumentieren verfügbare Endpunkte; sie beweisen nicht die konkrete Anbieter-
  oder Quantisierungswahl jeder Anfrage. Keine BF16-Serving-Replikation von Arete.
- Apertus/Kolibri: Proxy-Routen ohne unabhängig verifizierte unveränderliche
  Gewichtsrevision im Snapshot. Unterschiedliche Modellgrößen und Serving-Konfigurationen.
- Judge Grok 4.7, ursprüngliche englische Frage/Fakten/Marker, Antwort in EN oder DE,
  Temperatur 0 und maximal 4.096 Ausgabetoken. Wörtliche Belege, Faktenpartition
  und Score-Konsistenz zusätzlich deterministisch validiert.
- Ein Lauf, keine Schätzung der Schwankung zwischen Läufen; kein unabhängig
  kalibrierter mehrsprachiger Judge. Selektive Ausfälle und Übersetzungsfehler
  bleiben mögliche Verzerrungen. Keine DACH-Anpassung oder Nachtrainierung.
- Nous berichtet auf Englisch über fünf Läufe Arete 2,98/0,9 % und Qwen 2,32/22 %.
  Andere Fallmengen, Wiederholungszahlen und Protokollabweichungen verhindern eine
  exakte Replikationsbehauptung. Unsere primäre Auswertung imputiert keine Nullwerte.

## Daten und Reproduktion

- [Vergleich](comparison.json): genaue Fallmengen, Aggregate, Transferdifferenzen,
  Fragetypen und Diagnosezahlen.
- [Gültige Einzelfälle](cases.jsonl): alle gültigen Einzelbewertungen, auch außerhalb
  der gepaarten Schnittmengen.
- [Alle Status](status.jsonl): 6.424 Bedingungen mit Einschlussstatus,
  Ausschlussgründen und Anzahl gespeicherter Versuche.
- Run-Snapshots und finale Antworten/Urteile: [Arete](../arete-01/),
  [Qwen](../qwen-01/), [Apertus/Kolibri](../main-01/), jeweils unter `release/`.
  `release/attempts.jsonl` enthält Status, Zeiten, Request- und Datei-Prüfsummen
  der gespeicherten Versuche. Die vollständigen lokalen Versuchdateien bleiben erhalten.
  `release/grades.jsonl` hält ursprüngliche Urteile, `grade-repairs.jsonl` die
  getrennten Korrekturen und `selected-grades.jsonl` die ausgewählten Bewertungen.
- [Übersetzungsmethode und Quellen](../../METHOD.md),
  [Nous Arete](https://nousresearch.com/arete),
  [OpenRouter-Modellmetadaten](../qwen-01/openrouter-model-metadata.json).

```sh
python3 scripts/evaluate.py report --run eval/arete-01
python3 scripts/evaluate.py report --run eval/qwen-01
python3 scripts/evaluate.py report --run eval/main-01
python3 scripts/export_evaluation_release.py --run eval/arete-01
python3 scripts/export_evaluation_release.py --run eval/qwen-01
python3 scripts/export_evaluation_release.py --run eval/main-01
python3 scripts/export_article_comparison.py
python3 scripts/write_comparison_report.py
python3 scripts/update_article_results.py --site /pfad/zur/namche.ai
```

Diese Exportbefehle verwenden die lokalen Originaldateien des Laufs.
Die veröffentlichten `release/`-Exporte und `cases.jsonl` erlauben eine
unabhängige Nachberechnung der Tabellen ohne neue Modellanfragen.
Der Übersetzungsrelease v1.0.0 und seine damaligen Ergebnisse bleiben unter
dem bestehenden Tag unverändert.
