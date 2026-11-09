# Protokoll: gepaarte EN-DE-Evaluation

## Fragestellung und Umfang

Überträgt sich Aretes gegenüber Qwen beobachteter Vorteil auf deutsche Fragen?
Wir vergleichen Arete und Qwen auf denselben 803 Fragen in Englisch und Deutsch.
Apertus und Kolibri ergänzen den Sprachvergleich. Insgesamt sind es 6.424
Antwortbedingungen, mit einem Lauf je Modell und Sprache.

Die Übersetzung und Referenzrubrik wurden vor der Antwortgenerierung eingefroren.
Jeder Run enthält `en.jsonl`, `de.jsonl`, `judge.md`, ein Manifest und SHA-256-Prüfsummen.
Die Übersetzung wurde nicht an deutsche, österreichische oder schweizerische
Rechtsverhältnisse angepasst. Es wurde kein Modell nachtrainiert.

## Antwortgenerierung

Jede Frage ist eine einzelne Nutzernachricht ohne zusätzliche angeforderte
Systemnachricht oder Tools. Referenzfakten und Übersetzungshinweise werden den
Antwortmodellen nicht gezeigt. Temperatur 0, maximal 32.768 Ausgabetoken.
Die Reihenfolge EN/DE wechselt je Frage; Parallelisierung kann die tatsächliche
Abschlussreihenfolge verändern. Modellkennungen, Requests, Zeiten, Status und
Antworten werden gespeichert.

| Modell | Snapshot | Serving und Thinking |
| --- | --- | --- |
| `arete-27b` / `NousResearch/Arete-27B` | `arete-01` | BF16, vLLM 0.32.0, eine RTX PRO 6000 96 GB, Kontext 65.536, Thinking aus |
| `qwen/qwen3.8-27b` | `qwen-01` | OpenRouter über Namche-Gateway, `reasoning.enabled=false` |
| `publicai/apertus-8b-instruct` | `main-01` | Proxy-Route, Anbieterdefaults außer expliziten Generierungsparametern |
| `alephalpha/kolibri-1-tl5` | `main-01` | Proxy-Route, Anbieterdefaults außer expliziten Generierungsparametern |

Arete verwendet Revision `108f0afbdcfaa1ceeda4a635004304dfff6d4da2` und
Container `docker.io/vllm/vllm-openai:v0.32.0` mit Digest
`sha256:6ee133356d49ed24cee03dd0cda3d3980279a11c107ce3e752c89e76540f41c9`.
Die maximale Replikenzahl ist eins; nach den Anfragen wird Scale-to-zero geprüft.

Qwens öffentliche [Modell- und Anbieter-Metadaten](qwen-01/openrouter-model-metadata.json)
sowie der [Routing-Snapshot](qwen-01/routing-provenance.json) sind separat gespeichert.
Sie dokumentieren verfügbare Anbieter und Quantisierungen, aber nicht zwingend
jede konkrete Anbieterwahl. Eine öffentliche Hub-Revision ist kein Nachweis der
vom Anbieter verwendeten Gewichtsrevision. Alle 1.606 Qwen-Antworten melden null
Reasoning-Tokens. Für Apertus/Kolibri wurde keine unveränderliche Gewichtsrevision
unabhängig verifiziert. Die Serving-Unterschiede verhindern eine ausschließliche
kausale Zuschreibung der Ergebnisse zum Arete-Training.

## Judge und Validierung

`x-ai/grok-4.7` bewertet alle Antworten bei Temperatur 0 und maximal 4.096
Ausgabetoken mit der unveränderten englischen Originalrubrik. Das ist mehr als
das 1.000-Token-Limit des Referenzskripts, damit strukturierte Urteile nicht
unnötig abgeschnitten werden. Der Judge erhält in beiden Sprachbedingungen
dieselbe englische Frage, Referenzfakten und Rahmungsmarker. Nur die Antwort
wechselt die Sprache. Es gibt keine Rückübersetzung und keine Modellkennung
im Judge-Prompt. Keines der Antwortmodelle bewertet sich selbst.

Die Rubrik liefert einen Faktenscore von 0 bis 5 und Propagandawerte von 0 bis 2.
Zusätzlich wird deterministisch geprüft:

- Die Faktenlisten partitionieren die exakten Referenzfakten.
- Der Score stimmt mit den Faktenanzahlen und der Original-Scoringregel überein.
- Propaganda-Markierungen sind durch wörtliche Zitate aus der Antwort belegt.
- Eine als Verweigerung markierte Antwort behauptet oder bestreitet keine Referenzfakten.

Ein ungültiges Urteil ist kein gültiger Nullscore. Scores werden nicht aus
widersprüchlichen Faktenlisten nachträglich zurechtgerechnet. Gegenüber dem
Referenzgrader prüfen wir somit zusätzlich die im Originalprompt geforderten
Konsistenzbedingungen. Die mehrsprachige Bewertungsqualität des Judges wurde
nicht unabhängig durch menschliche Urteile kalibriert.

## Wiederaufnahme und Ausfälle

Gültige Antworten und Urteile bleiben erhalten. Fehlende oder technisch/formal
ungültige Aufrufe können mit unveränderten fachlichen Requests wiederholt werden.
Der abschließende Reparaturlauf erlaubt je Ziel bis zu zwei zusätzliche Versuche.
Neu nachgeholte Antworten werden anschließend bewertet. Requests und alle
Versuche bleiben lokal erhalten; finale Exporte enthalten auch Fehlerstatus
und separate Versuchsmetadaten. Änderungen an Modell, Prompt oder Parametern
benötigen einen neuen Snapshot.

Bei verbleibenden formalen Fehlern wird ein separater Korrekturschritt verwendet:
Der Judge erhält seinen ursprünglichen Request, sein bisheriges Urteil und den
[veröffentlichten Validierungshinweis](../prompts/judge-validation-repair.md).
Dieser hebt die bestehende Priorität „genau ein Fakt fehlt = 4“ sowie wörtliche
Zitate einschließlich Markdown hervor. Rubrik, Modell, Temperatur und Tokenlimit
bleiben gleich; der Gesprächsverlauf ist erweitert. Originale und Korrekturen
werden getrennt gespeichert. Nur validierte Korrekturen mit passender Prüfsumme
des ursprünglichen Urteils werden ausgewählt. Für die primäre Schnittmenge wird
zusätzlich eine Auswertung ohne diesen Korrekturschritt veröffentlicht.

Der Judge wird per Streaming mit Usage-Informationen angefragt. Für frische
Versuche wird der Proxy-Cache explizit mit `no-cache` und `no-store` umgangen.
Der Transportweg kann als dokumentierter Override denselben öffentlichen
Gateway verwenden, ohne das fachliche Request-Fingerprint zu verändern.
Dauerhaft ungültige Urteile, technische Fehler und am Tokenlimit abgeschnittene
Antworten bleiben von der primären Auswertung ausgeschlossen.

## Auswertung

Primär verwenden wir die Schnittmenge gültiger Arete-EN-, Arete-DE-, Qwen-EN-
und Qwen-DE-Bewertungen. Alle vier Werte werden auf dieser identischen
Fallmenge neu berechnet. Faktenscore-Gewinn ist `Arete − Qwen`.
Propaganda-Verringerung ist `Anteil Qwen − Anteil Arete`, in Prozentpunkten.
Für beide wird zusätzlich `Gewinn DE − Gewinn EN` berichtet.

Der Vergleich aller vier Modelle verwendet die Schnittmenge aller acht
Bedingungen. Modellbezogene EN-DE-Tabellen verwenden dagegen die jeweils
vollständigen Sprachpaare. Fragetypen werden separat ausgewiesen;
Themenkategorien können überlappen. Einschlussstatus und ausgeschlossene IDs
werden veröffentlicht. Primär gibt es keine Nullimputation. `report.json`
enthält zusätzlich eine ausdrücklich bezeichnete, an der Originalkonvention
orientierte Nullimputation als Sensitivitätsdarstellung.

Ein als vollständig markierter Run verlangt alle 803 Paare. Ein abgeschlossener
Reparaturlauf kann trotzdem ungültige und ausgeschlossene Fälle enthalten.
Es gibt keine Schätzung der Schwankung zwischen unabhängigen Läufen und keine
ungeprüfte Signifikanzbehauptung. Fehlende Bewertungen können selektiv sein.
Die Ergebnisse gelten für diese Rubrik und Themenauswahl, nicht für politische
Neutralität insgesamt oder DACH-Rechtstauglichkeit.

## Reproduktion und Quellen

Die [Ergebnisdokumentation](article-comparison/README.md) enthält Auswertung,
Datenverweise und Befehle für die lokale Nachberechnung. Run-Manifeste bleiben
unverändert. Die veröffentlichten finalen Antworten, Urteile und Falllisten
ermöglichen eine unabhängige Prüfung ohne neue Modellanfragen.

- [Nous: Arete](https://nousresearch.com/arete): fünf Läufe, teilweise andere
  Temperaturen und Ausfallkonventionen. Unsere Werte sind keine exakte Replikation.
- [Originaldatensatz](https://huggingface.co/datasets/NousResearch/Propaganda_Eval/tree/401223a2bfcdcd99d4650a83c4d20565db0e56b8):
  User-Turn, Rubrik und Scoring; unveränderte Kopien unter `upstream/`.
- [Übersetzungsmethode und Best Practices](../METHOD.md).
- [LiteLLM Cache Controls](https://docs.litellm.ai/docs/proxy/caching_controls).
