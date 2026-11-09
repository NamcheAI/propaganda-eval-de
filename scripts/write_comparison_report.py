"""Write result documentation from the validated comparison export."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'eval/article-comparison'


def num(value):
    return f'{value:.3f}'.replace('.', ',')


def table(models, sample):
    lines = ['| Modell | Sprache | n | Faktenscore (0 bis 5) | Propaganda | Verweigerungen |',
             '| --- | --- | ---: | ---: | ---: | ---: |']
    for name, values in models.items():
        for lang in ('en', 'de'):
            a, n = values[lang], values['n']
            lines.append(f"| {name} | {lang.upper()} | {n} | {num(a['fact_mean'])} | {a['propaganda_count']}/{n} ({num(a['propaganda_count']/n*100)} %) | {a['refusal_count']}/{n} |")
    return '\n'.join(lines)


def main():
    d = json.loads((OUT / 'comparison.json').read_text())
    p = d['primary_transfer']
    individual = {m['name']: m['paired'] for m in d['models']}
    shared = {m['name']: m['shared'] for m in d['models']}
    gains = p['gains']
    groups = ['| Fragetyp | Gemeinsame Fragen | Qwen EN | Qwen DE | Arete EN | Arete DE |',
              '| --- | ---: | ---: | ---: | ---: | ---: |']
    for label, group in p['by_question_type'].items():
        models = group['models']
        groups.append(f"| {label} | {len(group['ids'])} | " + ' | '.join(num(models[m][lang]['fact_mean']) for m in ('Qwen', 'Arete') for lang in ('en', 'de')) + ' |')
    status = [json.loads(line) for line in (OUT/'status.jsonl').read_text().splitlines()]
    raw = p['without_validation_feedback']
    failed = ['| Modell | Sprache | Gültig bewertet | Ungültiges Urteil | Fehlendes Urteil | Abgeschnittene Antwort |',
              '| --- | --- | ---: | ---: | ---: | ---: |']
    for m in d['models']:
        for lang in ('en', 'de'):
            rows = [r for r in status if r['model'] == m['model'] and r['language'] == lang]
            failed.append(f"| {m['name']} | {lang.upper()} | {sum(r['included'] for r in rows)} | {sum(r['grade_status'] == 'technical_error' for r in rows)} | {sum(r['grade_status'] == 'missing' and r['answer_status'] == 'ok' for r in rows)} | {sum(r['answer_status'] == 'truncated' for r in rows)} |")
    text = f'''# Arete, Qwen, Kolibri und Apertus: EN-DE-Vergleich

803 eingefrorene Fragen pro Modell und Sprache, ein Lauf, Ergebnisstand nach
gezielter Wiederholung fehlender oder technisch/formal ungültiger Aufrufe.
Alle Zahlen folgen der ursprünglichen Bewertungsrubrik. Der Faktenscore ist
keine allgemeine Wahrheitsquote; Propaganda bezeichnet deren konkrete Marker.

## Primärfrage: Aretes Vorteil gegenüber Qwen in beiden Sprachen

**{p['n']} identische Fragen** mit gültigen Bewertungen in allen vier Bedingungen.
{803-p['n']} Fragen bleiben ausgeschlossen. Die Fallmenge ist für alle vier Zeilen identisch.

{table(p['models'], 'primary')}

| Vorteil Aretes gegenüber Qwen | Englisch | Deutsch | Deutsch minus Englisch |
| --- | ---: | ---: | ---: |
| Höherer Faktenscore | {num(gains['en']['fact_gain'])} | {num(gains['de']['fact_gain'])} | {num(p['difference_de_minus_en']['fact_gain'])} |
| Verringerung des Propaganda-Anteils, Prozentpunkte | {num(gains['en']['propaganda_reduction_percentage_points'])} | {num(gains['de']['propaganda_reduction_percentage_points'])} | {num(p['difference_de_minus_en']['propaganda_reduction_percentage_points'])} |

Arete zeigt auch auf Deutsch einen höheren Faktenscore und weniger
Propaganda-Markierungen als Qwen. Der deutsche Faktenscore liegt bei beiden
Modellen niedriger. Das beschreibt diesen Lauf, ohne Signifikanz- oder
Kausalnachweis: Hosting und Quantisierung sind nicht vollständig angeglichen.

Ohne zusätzliche Validierungsrückmeldung umfasst die primäre Schnittmenge
{raw['n']} Fragen. Diese Sensitivitätsauswertung steht mit allen Einzelwerten
unter `primary_transfer.without_validation_feedback` in `comparison.json`.

### Faktenscores nach Fragetyp, gleiche vier Bedingungen

{chr(10).join(groups)}

## Alle vier Modelle auf denselben Fragen

**{len(d['shared_ids'])} gemeinsame Fragen** in allen acht Bedingungen;
{len(d['shared_excluded_ids'])} Fragen ausgeschlossen. Diese Fallmenge unterscheidet
sich von der primären Arete-Qwen-Auswertung.

{table(shared, 'shared')}

## Jeweils vollständige Sprachpaare pro Modell

Diese Zahlen verwenden unterschiedliche Fallmengen und sind nicht für eine
direkte Rangliste gedacht. Verweigerungen sind automatische Judge-Labels.

{table(individual, 'paired')}

## Ausfälle und Wiederholungen

{chr(10).join(failed)}

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
'''
    (OUT/'README.md').write_text(text)
    readme = ROOT/'README.md'
    s=readme.read_text()
    anchor = 'Der [EN-DE-Vergleich mit vier Modellen]' if 'Der [EN-DE-Vergleich mit vier Modellen]' in s else 'Der [erste Arete-Vergleich]'
    a=s.index(anchor); b=s.index('Die [Evaluation]',a)
    summary=f'''Der [EN-DE-Vergleich mit vier Modellen](eval/article-comparison/README.md) ist ausgewertet.
Alle 803 Fragen wurden je Modell in beiden Sprachen gestellt. Auf den **{p['n']} identischen
Arete-Qwen-Fällen** erreicht Arete auf Deutsch einen um **{num(gains['de']['fact_gain'])} Punkte**
höheren Faktenscore und **{num(gains['de']['propaganda_reduction_percentage_points'])} Prozentpunkte**
weniger Propaganda-Markierungen als Qwen. Das ist ein deskriptiver Befund des ersten Laufs;
unterschiedliches Serving begrenzt die Zuschreibung zum Training. Wir haben kein Modell nachtrainiert.

Der Gesamtvergleich mit Apertus und Kolibri verwendet **{len(d['shared_ids'])} identische Fragen**
in allen acht Bedingungen. Ungültige Bewertungen und abgeschnittene Antworten bleiben
ausgeschlossen. Daten, exakte Fallmengen und Grenzen stehen im
[Ergebnisbericht](eval/article-comparison/README.md) und in den
[Vergleichsdaten](eval/article-comparison/comparison.json).

'''
    s=s[:a]+summary+s[b:]
    s=s.replace('Ein erster Arete-Sprachvergleich liegt vor; ein vollständiger Arete-Qwen-Vergleich steht aus.',
                'Ein erster gepaarter Arete-Qwen-Sprachvergleich sowie Apertus- und Kolibri-Baselines liegen vor.')
    readme.write_text(s)
    for run, names in [('arete-01',['Arete']),('qwen-01',['Qwen']),('main-01',['Apertus','Kolibri'])]:
        models={name:individual[name] for name in names}
        (ROOT/'eval'/run/'README.md').write_text(f'''# {', '.join(names)}: EN-DE-Lauf 01

803 eingefrorene Fragen je Sprache und Modell, ein Lauf.
Finaler Stand nach gezielter Wiederholung fehlender oder ungültiger Aufrufe.

{table(models, 'paired')}

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
''')
    print('Updated comparison report and run documentation.')


if __name__ == '__main__':
    main()
