---
license: mit
language:
- de
- en
pretty_name: Propaganda Eval DE
size_categories:
- n<1K
task_categories:
- question-answering
configs:
- config_name: de
  data_files:
  - split: test
    path: data/items.jsonl
  default: true
- config_name: en
  data_files:
  - split: test
    path: upstream/data/items.jsonl
---

# Propaganda Eval DE

Deutsche Übersetzung der 803 Eval-Items aus
[NousResearch/Propaganda_Eval](https://huggingface.co/datasets/NousResearch/Propaganda_Eval),
herausgegeben von [here-be-dragons-ai](https://github.com/here-be-dragons-ai).

## Vorgehen

1. Übersetzen mit **GPT-6 Astra, high**.
2. Gegen das englische Original prüfen mit **Claude Fable 5.1, medium**.
3. Menschliche Entscheidungen übernehmen und verbleibende Hinweise durch beauftragte KI-Einzelprüfung entscheiden.
4. Entscheidungen dokumentieren, die finale Fassung validieren und für die Evals einfrieren.

[Methodik und Quellen](METHOD.md) · [Übersetzungsprompt](prompts/translate.md) · [Reviewprompt](prompts/review.md)

Die tatsächlich verwendeten Prompts dieses Laufs liegen unter [prompts/v1](prompts/v1).
Die aktuellen Prompts enthalten zusätzlich die freigegebene deutsche Zahlenformatierung.

## Ergebnisse

Alle **803 Items sind final adjudiziert und für den ersten Eval-Lauf eingefroren**.
Alle 670 Prüfpunkte einschließlich der nachträglich eingegangenen Hinweise sind entschieden.
Es liegen 39 menschliche Entscheidungen, 617 KI-Entscheidungen und 14 Anwendungen der Zahlenregel vor.
Eine separate redaktionelle Korrektur behebt einen Flexionsfehler. Dies ist eine gemischte
Adjudikation, keine vollständige unabhängige menschliche Validierung.
Der Astra-Aufruf enthält zusätzlich den dokumentierten
[Provider-Systemtext](prompts/translate-provider.txt).

[Finaler Prüfbericht](results/FINAL_REVIEW.md) · [Release-Manifest](results/release-manifest.json)

| Datei | Inhalt |
| --- | --- |
| [data/items.jsonl](data/items.jsonl) | Finale deutsche Übersetzung v1.0 |
| [upstream/data/items.jsonl](upstream/data/items.jsonl) | Englisches Original |
| [results/status.json](results/status.json) | Abschlussstatus des ursprünglichen Modelllaufs |
| [results/HUMAN_REVIEW.md](results/HUMAN_REVIEW.md) | Ursprüngliche Prüfpunkte mit vollständigem Kontext; aktuelle Entscheidungen im Interface |
| [results/reviews.jsonl](results/reviews.jsonl) | Modellbefunde und Korrekturvorschläge |
| [results/human-decisions.jsonl](results/human-decisions.jsonl) | Menschliche Entscheidungen |
| [results/agent-decisions.jsonl](results/agent-decisions.jsonl) | Beauftragte KI-Einzelfallentscheidungen, getrennt von menschlicher Prüfung |
| [results/agent-research.jsonl](results/agent-research.jsonl) | Recherche, Quellenzugriff und Vorher/Nachher je Minor-Befund |
| [results/final-review.jsonl](results/final-review.jsonl) | Entscheidungen zu den verbleibenden 274 Hinweisen |
| [results/working-translation.jsonl](results/working-translation.jsonl) | Arbeitsfassung; beim Release identisch mit der finalen Fassung |
| [results/policy-application.json](results/policy-application.json) | Zahlenregel, Eingabeprüfsummen und geänderte Felder des letzten Exports |
| [results/policy-decisions.jsonl](results/policy-decisions.jsonl) | Durch die Zahlenregel erledigte Hinweise des letzten Exports |
| [results/batches.jsonl](results/batches.jsonl) | Modelle, Parameter, Zeitstempel und Prüfsummen pro Batch |

Die Übersetzung erhält die Fragen, Fakten und politische Rahmung des Originals. Sie ergänzt keine
DACH-Fälle und ist keine Validierung für den deutschen, österreichischen oder schweizerischen Rechtsraum.
Prüfpunkte sind keine bestätigten Fehler; unmarkierte Items können ebenfalls Fehler enthalten.
Der unveränderte Modelloutput bleibt in `results/translated.jsonl` erhalten.
Die finale Fassung steht in `data/items.jsonl` und `results/adjudicated.jsonl`.
Der EN-DE-Snapshot unter `eval/arete-01/` enthält alle 803 Paare und das Adjudikationsmanifest.

## Experten-Interface und Evaluation

Die [lokale Expertenprüfung](review-ui/README.md) bietet Original, Übersetzung, Vorschläge und
dokumentierte Entscheidungen: `python3 scripts/review_ui.py`.

Der [EN-DE-Vergleich mit vier Modellen](eval/article-comparison/README.md) ist ausgewertet.
Alle 803 Fragen wurden je Modell in beiden Sprachen gestellt. Auf den **803 identischen
Arete-Qwen-Fällen** erreicht Arete auf Deutsch einen um **0,747 Punkte**
höheren Faktenscore und **23,661 Prozentpunkte**
weniger Propaganda-Markierungen als Qwen. Das ist ein deskriptiver Befund des ersten Laufs;
unterschiedliches Serving begrenzt die Zuschreibung zum Training. Wir haben kein Modell nachtrainiert.

Der Gesamtvergleich mit Apertus und Kolibri verwendet **802 identische Fragen**
in allen acht Bedingungen. Ungültige Bewertungen und abgeschnittene Antworten bleiben
ausgeschlossen. Daten, exakte Fallmengen und Grenzen stehen im
[Ergebnisbericht](eval/article-comparison/README.md) und in den
[Vergleichsdaten](eval/article-comparison/comparison.json).

Die [Evaluation](eval/PROTOCOL.md) enthält Runner und Protokoll. Der ältere
[technische Pilot](eval/pilot-01/README.md) diente der Funktionsprüfung.

## Ausführen

Python 3.12 oder neuer. Für Übersetzungen: `.env` mit `INFERENCE_API_KEY` für `https://inference.namche.net`.
Die Fable-Route unterstützt den hinterlegten Subscription-/Setup-Token über Claude Code.
Ein Minimaltest ist mit `python3 scripts/check_subscription.py` möglich (Claude Code 2.1.308).
Der Test verwendet den Gateway-Key aus `.env`; ein separater Anthropic-API-Key ist nicht erforderlich.
Der Review verwendet denselben Transport mit `--bare --safe-mode` und deaktivierten Tools.

```sh
python3 scripts/run.py --translate-only
python3 scripts/run.py
python3 scripts/validate.py
python3 scripts/finalize.py results
```

Bereits vorhandene Ergebnisse werden wiederverwendet. Die Finalisierung benötigt einen vollständigen
Modellreview und dokumentierte Entscheidungen zu allen offenen Prüfpunkten.

## Herkunft und Lizenz

Originalrevision: `401223a2bfcdcd99d4650a83c4d20565db0e56b8`. Original und Übersetzung: MIT.
Unabhängige Ableitung ohne Zugehörigkeit zu Nous Research. Ein erster gepaarter Arete-Qwen-Sprachvergleich sowie Apertus- und Kolibri-Baselines liegen vor.
