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
3. Unsicherheiten und Änderungsvorschläge durch den Auftraggeber oder hinzugezogene Fachleute entscheiden lassen.
4. Entscheidungen dokumentieren und die finale Fassung validieren.

[Methodik und Quellen](METHOD.md) · [Übersetzungsprompt](prompts/translate.md) · [Reviewprompt](prompts/review.md)

## Ergebnisse

803 Items sind übersetzt; 785 sind modellgeprüft, 18 Reviews stehen noch aus. Die Fassung ist noch nicht
menschlich freigegeben. Der Astra-Aufruf enthält zusätzlich den dokumentierten
[Provider-Systemtext](prompts/translate-provider.txt).

| Datei | Inhalt |
| --- | --- |
| [data/items.jsonl](data/items.jsonl) | Deutsche Übersetzung |
| [upstream/data/items.jsonl](upstream/data/items.jsonl) | Englisches Original |
| [results/status.json](results/status.json) | Aktueller Prüfstatus |
| [results/HUMAN_REVIEW.md](results/HUMAN_REVIEW.md) | Offene Prüfpunkte mit vollständigem Kontext |
| [results/reviews.jsonl](results/reviews.jsonl) | Modellbefunde und Korrekturvorschläge |
| [results/human-decisions.jsonl](results/human-decisions.jsonl) | Menschliche Entscheidungen |
| [results/batches.jsonl](results/batches.jsonl) | Modelle, Parameter, Zeitstempel und Prüfsummen pro Batch |

Die Übersetzung erhält die Fragen, Fakten und politische Rahmung des Originals. Sie ergänzt keine
DACH-Fälle und ist keine Validierung für den deutschen, österreichischen oder schweizerischen Rechtsraum.
Prüfpunkte sind keine bestätigten Fehler; unmarkierte Items können ebenfalls Fehler enthalten.

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
Unabhängige Ableitung ohne Zugehörigkeit zu Nous Research. Es wurden keine Modell-Benchmark-Ergebnisse
mit dieser deutschen Fassung erhoben.
