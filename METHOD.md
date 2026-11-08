# Methodik

## Material und Übersetzung

Wir übersetzen alle 803 Items der festgelegten Originalrevision von
[NousResearch/Propaganda_Eval](https://huggingface.co/datasets/NousResearch/Propaganda_Eval).
Übersetzt werden `prompt`, `required_facts`, `anchor` und vorhandene `official_frame_markers`.
IDs, Quellen, Kategorien, Fragetypen sowie Anzahl und Reihenfolge der Listeneinträge bleiben erhalten.

Die Erstübersetzung erfolgt mit `chatgpt/gpt-6-astra`, `reasoning_effort: high`, über
`https://inference.namche.net/v1/chat/completions`. Je Batch werden fünf aufeinanderfolgende Items
übergeben. Ausgabelimit: 24.000 Tokens; Temperatur, top_p und seed bleiben Anbieterdefaults.
Der [verwendete Übersetzungsprompt](prompts/v1/translate.md) priorisiert Bedeutungstreue, Zuschreibung, Negationen,
Gewissheitsgrade, politische Konnotationen und Terminologie. Die deutsche Fassung verwendet ß.
Fragen werden übersetzt, nicht beantwortet; Tatsachenbehauptungen werden nicht stillschweigend korrigiert.
Die verwendete ChatGPT-Route ergänzt den [Provider-Systemtext](prompts/translate-provider.txt)
aus LiteLLM 1.108.1. Dieser ist Bestandteil der effektiven Modellanfrage.

## Modellreview

Alle 803 Items wurden mit `anthropic/claude-fable-5-1`, `reasoning_effort: medium`, über denselben Gateway geprüft. Der
[verwendete Reviewprompt](prompts/v1/review.md) wird als Systemprompt verwendet. Der Reviewer erhält jeweils die
englischen Felder, die Astra-Übersetzung und deren Hinweise. Er sieht keine späteren menschlichen Entscheidungen.
Der Subscription-Zugang wurde mit Claude Code 2.1.308 über LiteLLM verifiziert.
Mit `--bare --safe-mode`, eigenem Systemprompt und deaktivierten Tools enthält die lokal
inspizierte Anfrage zusätzlich einen Abrechnungsblock und die Agentenidentität
`You are a Claude agent, built on Anthropic's Claude Agent SDK.`
Persönlicher Kontext und Umgebungsinstruktionen waren in dieser Anfrage nicht enthalten.
Der Review verwendet diesen Transport mit 24.000 maximalen Ausgabetokens und fünf Items pro Batch.
Die Modellaliases des Clients werden ausdrücklich auf die Fable-Route gesetzt.
Die tatsächlich gemeldete Modellkennung und Client-Version werden pro Batch protokolliert.
Die zusätzlich beobachteten Systemblöcke stehen in [review-provider.txt](prompts/review-provider.txt).
Der Versionssuffix im Abrechnungsblock ist clientgeneriert; die Datei dokumentiert die lokale
Inspektion und ist kein Mitschnitt jeder produktiven Anfrage.

Der Reviewer unterscheidet Übersetzungsfehler, vertretbare Entscheidungen und Stilpräferenzen.
Schweregrade: critical, major, minor oder none. Jede vorgeschlagene Änderung muss mit einem konkreten
Befund am Original verbunden sein. Die Vorschläge werden separat gespeichert und nicht automatisch übernommen.
Bei Quellen- und Übersetzungszitaten in Befunden werden ausschließlich abweichende Leerraumzeichen
deterministisch auf den Eingabetext zurückgeführt, wenn der übrige Text identisch ist.
Die Anzahl dieser Wiederherstellungen wird pro Batch protokolliert.
Nicht mit einem Befund begründete Textänderungen werden durch einen deterministischen Vergleich
als `undocumented_change` separat zur menschlichen Prüfung vorgelegt. Der Modelltext bleibt unverändert;
die Pipeline ergänzt keine vermeintliche Modellbegründung.
Dies ist eine separate Modellprüfung, keine blinde oder menschliche Bewertung.

## Menschliche Prüfung

### Freigegebene Zahlenregel

Der Auftraggeber hat die Regel [numbers-de-v1](policies/numbers-de.json) ausdrücklich freigegeben:
englisch `1,234` wird deutsch `1.234`, `1.23` wird `1,23`, `1,234.56` wird `1.234,56`.
Zahlenwerte und Einheiten bleiben erhalten. URLs, Datumsangaben und technische Identifikatoren
werden nicht nach dieser Regel geändert. Mehrdeutige Zuordnungen werden nicht geraten.

Die Regel wird deterministisch anhand der englischen Zahlen auf alle übersetzten Felder und
gespeicherten Feldentscheidungen angewandt. Die ursprünglichen Modellantworten und menschlichen
Entscheidungseinträge bleiben unverändert. Das Interface zeigt die daraus abgeleitete Arbeitsfassung.
`scripts/apply_number_policy.py` exportiert diese als `results/working-translation.jsonl` und
dokumentiert Änderungen und Eingabeprüfsummen in `results/policy-application.json`.
Diese Exporte sind Momentaufnahmen; nach weiteren Entscheidungen können sie erneut erzeugt werden.

Reine Formatkorrekturvorschläge werden anhand des vollständigen Feldtexts erkannt. Bestehende
Hinweise ohne konkreten Vorschlag wurden einzeln auf diesen Umfang geprüft; ihre IDs sind in der
Regeldatei dokumentiert. Zusätzliche Bedeutungsfragen sowie explizit zurückgestellte menschliche
Entscheidungen bleiben offen. Automatische Erledigungen stehen separat in `results/policy-decisions.jsonl`;
sie sind keine zusätzlichen unabhängigen Expertenurteile. Alle sonstigen Entscheidungen bleiben Einzelfallentscheidungen.

Die aktuellen Prompts unter `prompts/translate.md` und `prompts/review.md` enthalten die Zahlenregel
für neue Läufe. Die unveränderten Prompts des abgeschlossenen Modelllaufs liegen unter `prompts/v1/`;
die Validierung prüft weiterhin ihre ursprünglichen Hashes. Neue Läufe prüfen Zahlenwerte unter
Berücksichtigung der freigegebenen Formatwechsel. Die Finalisierung wendet dieselbe Regel an.

### Einzelfallentscheidungen

Die Prüfliste enthält offene Unsicherheiten des Übersetzers, alle Reviewerbefunde, automatische Hinweise
auf veränderte Zahlen, chinesische Zeichen oder URLs sowie ausdrücklich benannte Fachfragen.
Jeder Prüfpunkt enthält Original, Übersetzung, Begründung, Quellen-URL und den vollständigen Item-Kontext.

Der Auftraggeber oder hinzugezogene Expertinnen und Experten dokumentieren je Prüfpunkt:

```json
{"issue_id":"ID aus der Prüfliste","decision":"accept|reject|modify|defer","reviewer":"Name oder stabile Kennung","reviewer_role":"Rolle oder Qualifikation","decided_at":"Datum mit Zeitzone","reason":"Begründung anhand des Originals","final_text":"vollständiger finaler Feldtext oder null","evidence":[]}
```

Unentschiedene, zurückgestellte oder widersprüchliche Fälle verhindern die Finalisierung.
Für die verbleibenden Minor-Befunde hat der Auftraggeber eine recherchierte KI-Einzelprüfung
durch Codex beauftragt. Diese Entscheidungen stehen getrennt in `results/agent-decisions.jsonl`;
je Befund dokumentiert `results/agent-research.jsonl` Original, Vorher/Nachher, Begründung,
Quellenzugriff und ergänzende Belege. Vorgehen und Ergebnis: [Minor-Prüfung](results/AGENT_REVIEW.md).
Dies ist eine beauftragte KI-Adjudikation, keine unabhängige menschliche Expertenvalidierung.
Für Release v1.0 hat der Auftraggeber die Entscheidung sämtlicher verbleibender Hinweise
einschließlich Zweifelsfällen an Codex delegiert. `results/final-review.jsonl` enthält diese
274 Schlussentscheidungen; Restunsicherheiten bleiben als solche dokumentiert, blockieren
nach der ausdrücklichen Schlussentscheidung aber nicht mehr die Finalisierung.
`results/editorial-corrections.jsonl` enthält eine genaue Vorher/Nachher-Korrektur der
Adjektivflexion in Fall 1363. Sie wird nur bei exakt passendem Ausgangstext angewandt,
ist als KI-Korrektur gekennzeichnet und verändert den menschlichen Originaleintrag nicht.
Menschliche Entscheidungen haben Vorrang. Eine spätere abweichende menschliche Entscheidung
zum selben Feld stellt betroffene KI-Befunde zur erneuten Prüfung zurück, ohne deren Originaleinträge
umzuschreiben. Bei gemischter Adjudikation heißt die finale Datei `adjudicated.jsonl`.

Die gezielte Prüfung markierter Stellen ergibt keine repräsentative Fehlerrate des Gesamtdatensatzes.
Für eine solche Aussage wären zusätzlich eine vorab ausgewählte Zufallsstichprobe einschließlich
unmarkierter Items und unabhängige qualifizierte menschliche Bewertungen erforderlich.

## Nachvollziehbarkeit

`results/config.json` dokumentiert die Konfiguration. `results/batches.jsonl` enthält pro Batch
Modellkennungen, Parameter, Zeitstempel, Tokenverbrauch sowie Hashes von Prompt, Eingabe und Ausgabe.
Die Tokenzahlen beziehen sich auf die übernommenen Batchantworten, nicht auf sämtliche Fehlversuche.
Die tatsächlichen Prompttexte stehen unter `prompts/`, Übersetzungen und Befunde unter `data/` und `results/`.
API-Schlüssel und lokale Laufcaches werden nicht veröffentlicht.

Automatische Prüfungen kontrollieren Struktur, Quellen- und Prompt-Hashes, Batchzuordnung sowie die
Vollständigkeit der Prüfliste. Wiederholungen erfolgen nur bei technischen oder strukturellen Fehlern,
mit unverändertem Eingabetext. Nach vier ungültigen JSON-Antworten oder Strukturfehlern wird ein Batch halbiert;
Prompt und Itemtexte bleiben gleich. Die tatsächliche Gruppierung steht im Batchmanifest. Modellaliases und Anbieterdefaults garantieren keine bitgenaue Wiederholbarkeit.
Die übersetzte Fassung wird vor einer späteren EN-DE-Benchmarkmessung eingefroren.
Release v1.0 ist in `data/items.jsonl` eingefroren. `results/release-manifest.json`
dokumentiert den Datenhash und `eval/main-01/` den vorbereiteten EN-DE-Lauf.

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
