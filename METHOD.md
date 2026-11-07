# Methodik

## Material und Übersetzung

Wir übersetzen alle 803 Items der festgelegten Originalrevision von
[NousResearch/Propaganda_Eval](https://huggingface.co/datasets/NousResearch/Propaganda_Eval).
Übersetzt werden `prompt`, `required_facts`, `anchor` und vorhandene `official_frame_markers`.
IDs, Quellen, Kategorien, Fragetypen sowie Anzahl und Reihenfolge der Listeneinträge bleiben erhalten.

Die Erstübersetzung erfolgt mit `chatgpt/gpt-6-astra`, `reasoning_effort: high`, über
`https://inference.namche.net/v1/chat/completions`. Je Batch werden fünf aufeinanderfolgende Items
übergeben. Ausgabelimit: 24.000 Tokens; Temperatur, top_p und seed bleiben Anbieterdefaults.
Der [Übersetzungsprompt](prompts/translate.md) priorisiert Bedeutungstreue, Zuschreibung, Negationen,
Gewissheitsgrade, politische Konnotationen und Terminologie. Die deutsche Fassung verwendet ß.
Fragen werden übersetzt, nicht beantwortet; Tatsachenbehauptungen werden nicht stillschweigend korrigiert.
Die verwendete ChatGPT-Route ergänzt den [Provider-Systemtext](prompts/translate-provider.txt)
aus LiteLLM 1.108.1. Dieser ist Bestandteil der effektiven Modellanfrage.

## Modellreview

`anthropic/claude-fable-5-1` soll mit `reasoning_effort: medium` über denselben Gateway prüfen. Der
[Reviewprompt](prompts/review.md) wird als Systemprompt verwendet. Der Reviewer erhält jeweils die
englischen Felder, die Astra-Übersetzung und deren Hinweise. Er sieht keine späteren menschlichen Entscheidungen.
Verwendet wird die API, ohne Agenten-CLI. Die tatsächlich gemeldete Modellkennung wird protokolliert.

Der Reviewer unterscheidet Übersetzungsfehler, vertretbare Entscheidungen und Stilpräferenzen.
Schweregrade: critical, major, minor oder none. Jede vorgeschlagene Änderung muss mit einem konkreten
Befund am Original verbunden sein. Die Vorschläge werden separat gespeichert und nicht automatisch übernommen.
Dies ist eine separate Modellprüfung, keine blinde oder menschliche Bewertung.

## Menschliche Prüfung

Die Prüfliste enthält offene Unsicherheiten des Übersetzers, alle Reviewerbefunde, automatische Hinweise
auf veränderte Zahlen, chinesische Zeichen oder URLs sowie ausdrücklich benannte Fachfragen.
Jeder Prüfpunkt enthält Original, Übersetzung, Begründung, Quellen-URL und den vollständigen Item-Kontext.

Der Auftraggeber oder hinzugezogene Expertinnen und Experten dokumentieren je Prüfpunkt:

```json
{"issue_id":"ID aus der Prüfliste","decision":"accept|reject|modify|defer","reviewer":"Name oder stabile Kennung","reviewer_role":"Rolle oder Qualifikation","decided_at":"Datum mit Zeitzone","reason":"Begründung anhand des Originals","final_text":"vollständiger finaler Feldtext oder null","evidence":[]}
```

Unentschiedene, zurückgestellte oder widersprüchliche Fälle verhindern die Finalisierung.
Die gezielte Prüfung markierter Stellen ergibt keine repräsentative Fehlerrate des Gesamtdatensatzes.
Für eine solche Aussage wären zusätzlich eine vorab ausgewählte Zufallsstichprobe einschließlich
unmarkierter Items und unabhängige qualifizierte menschliche Bewertungen erforderlich.

## Nachvollziehbarkeit

`results/config.json` dokumentiert die Konfiguration. `results/batches.jsonl` enthält pro Batch
Modellkennungen, Parameter, Zeitstempel, Tokenverbrauch sowie Hashes von Prompt, Eingabe und Ausgabe.
Die tatsächlichen Prompttexte stehen unter `prompts/`, Übersetzungen und Befunde unter `data/` und `results/`.
API-Schlüssel und lokale Laufcaches werden nicht veröffentlicht.

Automatische Prüfungen kontrollieren Struktur, Quellen- und Prompt-Hashes, Batchzuordnung sowie die
Vollständigkeit der Prüfliste. Wiederholungen erfolgen nur bei technischen oder strukturellen Fehlern,
mit unverändertem Eingabetext. Modellaliases und Anbieterdefaults garantieren keine bitgenaue Wiederholbarkeit.
Die übersetzte Fassung wird vor einer späteren EN-DE-Benchmarkmessung eingefroren.

## Quellen

- [Freitag et al. (2021), Experts, Errors, and Context](https://aclanthology.org/2021.tacl-1.87/):
  explizite Fehleranalyse durch qualifizierte Übersetzende mit ausreichend Kontext.
- [MQM Council, Uses of MQM](https://www.themqm.org/what-is-mqm/uses-of-mqm/):
  analytische Übersetzungsbewertung und menschliche Validierung automatischer Bewertungen.
- [Gebru et al. (2021), Datasheets for Datasets](https://arxiv.org/abs/1803.09010):
  Dokumentation von Herkunft, Erstellung, Verwendungszweck und Grenzen eines Datensatzes.
- [LiteLLM 1.108.1, ChatGPT-Adapter](https://github.com/BerriAI/litellm/blob/v1.108.1/litellm/llms/chatgpt/common_utils.py):
  Herkunft des zusätzlichen Provider-Systemtexts; MIT, Copyright 2023 Berri AI.

Unsere Fehlerkategorien sind MQM-orientiert, keine standardisierte MQM-Gesamtnote oder Zertifizierung.
Modellwahl und Batchgröße sind Projektentscheidungen, keine durch diese Quellen belegten Optima.
