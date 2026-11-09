"""Prepare the completed-run Namche article locally from reconciled result exports."""
import argparse
import json
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--site', type=Path, required=True)
    args = parser.parse_args()
    d = json.loads((ROOT / 'eval/article-comparison/comparison.json').read_text())
    models = {m['name']: m for m in d['models']}
    primary = d['primary_transfer']; n = primary['n']; shared = len(d['shared_ids'])
    baseline = primary['without_validation_feedback']
    def num(x, digits=3): return f'{x:.{digits}f}'.replace('.', ',')
    def pct(count, total): return num(count / total * 100)
    a, q, k, ap = (models[x]['paired'] for x in ['Arete', 'Qwen', 'Kolibri', 'Apertus'])
    g = primary['gains']; diff = primary['difference_de_minus_en']
    invalid = {name: sum(d['diagnostics'][name][lang]['grade_status'].get('technical_error', 0)
                        for lang in ('en', 'de')) for name in models}
    truncated = sum(arm['answer_status'].get('truncated', 0)
                    for model in d['diagnostics'].values() for arm in model.values())
    failures = [f"{count} ungültige {name}-Urteile" for name, count in invalid.items() if count]
    if truncated:
        failures.append(f"{truncated} am Tokenlimit unvollständige " + ('Antwort' if truncated == 1 else 'Antworten'))
    remaining = ("Nach den Wiederholungen verbleiben: " + '; '.join(failures) +
                 ". Diese Fälle sind in den Downloads ausgewiesen. Die gemeinsame Fallmenge "
                 "schließt sie aus; dadurch können die Ergebnisse verzerrt sein.") if failures else (
                 "Für alle vier Modelle liegen nun für sämtliche 803 Fragen in beiden Sprachen "
                 "vollständige Antworten und gültige Bewertungen vor.")
    primary_population = ("Alle **803 Fragen** wurden für Arete und Qwen in beiden Sprachen "
                          "gültig bewertet. Es gibt in diesem Vergleich keine ausgeschlossenen Fragen.") if n == 803 else (
                          f"Für die primäre Frage behalten wir nur die **{n} Fragen**, für die Arete und Qwen "
                          f"in beiden Sprachen gültig bewertet wurden. Damit entfallen {803-n} der 803 Fragen.")
    shared_exclusion = ("Keine Frage entfällt." if shared == 803 else
                        f"{'Eine Frage entfällt' if 803-shared == 1 else str(803-shared)+' Fragen entfallen'}.")
    site = args.site
    article = site / 'content/insights/arete-auf-deutsch.md'
    old = article.read_text()
    front = old.split('---', 2)[1].strip()
    lines=front.splitlines()
    lines=["title: 'Arete auf Deutsch: weniger chinesische Staatspropaganda als Qwen'" if x.startswith('title:') else x for x in lines]
    lines=["description: 'Chinesische Open-Weight-Modelle sind eine Chance für souveräne KI. Kann Post-Training politischen Bias verändern, und wirkt das auch auf Deutsch?'" if x.startswith('description:') else x for x in lines]
    body = f'''
Chinesische Open-Weight-Modelle wie Qwen sind eine leistungsfähige Alternative
zu den geschlossenen Modellen der großen Frontier-Labore. Ihre Gewichte lassen
sich herunterladen, auf eigener Infrastruktur betreiben und für eigene Zwecke
anpassen. Das macht sie zu einem wichtigen Baustein für souveräne KI: mehr
Kontrolle über Daten, Betrieb und Weiterentwicklung.

Doch auch ein selbst betriebenes Modell bringt die politische Prägung seines
Trainings mit. [Nous Research](https://nousresearch.com/arete) berichtet bei
Qwen3.8-27B von Verweigerungen, ausweichenden Antworten und chinesischen
Staatsnarrativen zu politisch sensiblen Themen. Wer ein solches Modell einsetzt,
übernimmt damit auch Verhaltensweisen, die den eigenen Anforderungen
widersprechen können. Lässt sich das durch gezieltes Post-Training verändern?

Genau das hat Nous Research mit **Arete-27B** untersucht. Das Team trainierte
Qwen3.8-27B auf rund 52,8 Millionen zusätzlichen Token nach, mit dem erklärten
Ziel, „westliche Werte“ zu stärken. Im eigenen englischen Test berichtet Nous
danach einen höheren Faktenscore und deutlich weniger Propaganda-Markierungen.
Das Modell, der Trainingsansatz und der ursprüngliche Test **Propaganda_Eval**
stammen von Nous Research.

„Propaganda“ bezeichnet im Folgenden die Übernahme oder Billigung chinesischer
Staatsnarrative nach der Rubrik dieses Tests. Die bloße Wiedergabe der offiziellen
Position mit klarer Zuschreibung zählt nicht dazu.

Aber bleibt eine solche Veränderung auch in einer anderen Sprache erhalten?
Ein besseres Ergebnis auf Englisch garantiert noch kein besseres Ergebnis auf
Deutsch. Hier setzt unsere Untersuchung an: **Bleibt Aretes Vorteil gegenüber
dem ursprünglichen Qwen auch bei denselben Fragen auf Deutsch sichtbar?**

Wir haben die 803 Fragen des Propaganda_Eval übersetzt und Arete, Qwen,
Kolibri und Apertus in beiden Sprachen getestet. Im gepaarten Vergleich mit Qwen
erreicht Arete auch auf Deutsch einen höheren Faktenscore und deutlich weniger
Propaganda-Markierungen. Der deutsche Faktenscore liegt bei beiden Modellen
unter dem englischen. Das ist der Befund dieses ersten Laufs unter der
verwendeten Bewertungsrubrik.

Den [Datensatz](https://huggingface.co/datasets/here-be-dragons-ai/propaganda-eval-de)
und [Methodik, Prompts und Ergebnisse](https://github.com/here-be-dragons-ai/propaganda-eval-de)
veröffentlichen wir bei [Here Be Dragons](https://here-be-dragons.ai).
Here Be Dragons ist eine Non-Profit-Organisation für verantwortungsvolle
Mensch-Maschine-Zukünfte. Wir haben kein Modell nachtrainiert.

[[image]]

## Was der Test misst

Der [Test von Nous Research](https://nousresearch.com/arete) enthält Referenzfakten
und konkrete Propaganda-Marker zu politisch sensiblen Fragen. Ein Judge-Modell
bewertet die Antworten anhand dieser Vorgaben. Der Faktenscore reicht von 0 bis 5
und erfasst, welche Referenzfakten genannt, ausgelassen oder widersprochen werden.
Er ist keine allgemeine Wahrheitsquote. Propaganda bedeutet hier eine Markierung
nach dieser Rubrik, keine umfassende Prüfung politischer Neutralität.

Der Datensatz bringt eine eigene Themenauswahl und politische Rahmung mit.
Unsere Übersetzung erhält beides. Die Fragen wurden nicht für deutsche,
österreichische oder schweizerische Rechtsverhältnisse umgeschrieben.

Nous berichtet auf Englisch für Arete 2,98 Faktenpunkte und 0,9 Prozent
Propaganda-Markierungen, für Qwen 2,32 Punkte und 22 Prozent. Das sind Mittelwerte
aus fünf Läufen. Unsere folgenden Ergebnisse stammen aus einem Lauf je Modell
und Sprache; fehlende Bewertungen werden nicht als Nullwerte ergänzt.

## Erst übersetzen, dann prüfen

GPT-6 Astra erstellte die Übersetzung bei Reasoning-Stufe high. Claude Fable 5.1
prüfte sie bei medium gegen das Original. Die Prompts, Modellparameter und
zusätzlichen Provider- beziehungsweise Client-Systemtexte liegen im Repository.

Alle 670 Prüfpunkte wurden dokumentiert entschieden: 39 durch Menschen,
617 durch beauftragte KI-Einzelfallprüfung und 14 nach der festgelegten Zahlenregel.
Hinzu kommt eine separat dokumentierte grammatische Korrektur. Zum Beispiel wird
englisch `1,234.56` zu deutsch `1.234,56`, ohne den Wert zu ändern.

Das Vorgehen orientiert sich am [MQM-Rahmen](https://themqm.org/) und an
[Datasheets for Datasets](https://arxiv.org/abs/1803.09010). Es ist eine gemischte
Prüfung durch Mensch und KI, keine vollständige unabhängige menschliche
Validierung oder MQM-Zertifizierung. Die [Methodik](https://github.com/here-be-dragons-ai/propaganda-eval-de/blob/main/METHOD.md)
beschreibt die Schritte und Grenzen.

## Derselbe Test in zwei Sprachen

Jedes Modell erhielt dieselben 803 Fragen auf Englisch und Deutsch, bei
Temperatur 0 und maximal 32.768 Ausgabetoken. Arete lief in BF16 auf einer
RTX PRO 6000 mit 96 GB und vLLM 0.32.0, mit festgehaltener Gewichtsrevision,
65.536 Token Kontext und deaktiviertem Thinking. Es erhielt keine zusätzliche
Systemnachricht.

Qwen3.8-27B wurde über OpenRouter und den Namche-Inference-Proxy angesprochen.
Thinking wurde mit `reasoning.enabled=false` ausgeschaltet; die gespeicherten
Tokenstatistiken dienen der Kontrolle. OpenRouter dokumentiert seine Modell-
und Anbieter-Endpunkte einschließlich Quantisierung. Diese öffentliche
Beschreibung ist von der tatsächlichen Endpunktwahl einer einzelnen Anfrage
zu unterscheiden. Qwen und Arete wurden nicht auf identischer Serving-Infrastruktur
betrieben; der Vergleich isoliert deshalb nicht ausschließlich das Arete-Training.

Für alle vier Modelle bewertete Grok 4.7 die Antworten mit der ursprünglichen
englischen Rubrik, Temperatur 0 und maximal 4.096 Ausgabetoken. Frage,
Referenzfakten und Propaganda-Marker blieben für den Judge auf Englisch, nur die
zu bewertende Antwort wechselte die Sprache. Seine sprachübergreifende
Bewertungsqualität wurde nicht unabhängig kalibriert.

Fehlende oder technisch beziehungsweise formal ungültige Aufrufe wurden gezielt
wiederholt. Erfolgreiche Antworten und gültige Urteile blieben bestehen.
Frühere Versuche und verbleibende Ausfälle bleiben dokumentiert. Faktenscore,
Faktenzuordnung und Belegzitate müssen die unveränderte Validierung bestehen.
Bei verbleibenden formalen Fehlern erhielt derselbe Judge sein bisheriges Urteil
und eine [standardisierte Validierungsrückmeldung](https://github.com/here-be-dragons-ai/propaganda-eval-de/blob/main/prompts/judge-validation-repair.md).
Rubrik und Modellparameter blieben gleich; Original und Korrektur sind getrennt
gespeichert. Die Downloads enthalten zusätzlich die Auswertung ohne diesen Schritt.
Sie umfasst {baseline['n']} gemeinsame Arete-Qwen-Fälle und zeigt ebenfalls einen
höheren deutschen Faktenscore und weniger Propaganda-Markierungen bei Arete.

## Qwen auf Deutsch

Für Qwen liegen **{q['n']} vollständige Sprachpaare** vor. Der Faktenscore beträgt
{num(q['en']['fact_mean'])} auf Englisch und {num(q['de']['fact_mean'])} auf Deutsch.
Propaganda-Markierungen betreffen {q['en']['propaganda_count']} englische Antworten
({pct(q['en']['propaganda_count'], q['n'])} Prozent) und
{q['de']['propaganda_count']} deutsche Antworten
({pct(q['de']['propaganda_count'], q['n'])} Prozent).

[[eval:qwen]]

Im ersten Lauf liegt Qwens deutscher Faktenscore unter dem englischen;
der Anteil der Propaganda-Markierungen liegt höher. Die folgende Gegenüberstellung
mit Arete verwendet dieselben Fragen für alle vier Bedingungen.

## Arete auf Deutsch

Für Arete liegen **{a['n']} vollständige Sprachpaare** vor. Auf dieser Fallmenge
beträgt der Faktenscore {num(a['en']['fact_mean'])} auf Englisch und
{num(a['de']['fact_mean'])} auf Deutsch. Der Judge markiert
{a['en']['propaganda_count']} englische und {a['de']['propaganda_count']} deutsche
Antworten als Propaganda.

[[eval:arete]]

Der englische Lauf liegt in einer ähnlichen Größenordnung wie das veröffentlichte
Nous-Ergebnis. Es ist keine exakte Replikation: Nous mittelt fünf Läufe, wir
berichten einen Lauf mit {a['n']} vollständigen Sprachpaaren. Die kleinen
Propaganda-Ereigniszahlen allein belegen keinen allgemeinen Vorteil einer Sprache.

## Bleibt Aretes Vorteil gegenüber Qwen erhalten?

{primary_population}
Alle vier Bedingungen in diesem Block verwenden genau diese identischen Fälle.

[[eval:transfer]]

Aretes Gewinn beim Faktenscore gegenüber Qwen beträgt auf Englisch
**{num(g['en']['fact_gain'])} Punkte**, auf Deutsch **{num(g['de']['fact_gain'])} Punkte**.
Die Differenz dieser Gewinne (Deutsch minus Englisch) beträgt
{num(diff['fact_gain'])} Punkte.

Der Anteil der Propaganda-Markierungen sinkt gegenüber Qwen auf Englisch um
**{num(g['en']['propaganda_reduction_percentage_points'])} Prozentpunkte** und auf
Deutsch um **{num(g['de']['propaganda_reduction_percentage_points'])} Prozentpunkte**.
Die Differenz dieser Verringerungen beträgt
{num(diff['propaganda_reduction_percentage_points'])} Prozentpunkte.

[[eval:design]]

[[eval:europe]]

Europäische Entwicklung und eigener Betrieb sind wichtige Schritte zu mehr
Unabhängigkeit. Doch auch hier stellt sich die Frage, welche politischen
Prägungen ein Modell mitbringt. Dazu gehört ein Blick auf die Trainingsgeschichte:
Viele Modelle lernen auch aus Antworten anderer KI-Systeme. Solche
**Tutormodelle** liefern synthetische Trainingsbeispiele und können damit
neben Fähigkeiten auch Antwortmuster weitergeben.

**Kolibri 1** stammt von Aleph Alpha aus Heidelberg und wurde im Oktober 2026
veröffentlicht. Es ist ein eigenständig vortrainiertes Modell für Deutsch und
Englisch mit rund 78 Milliarden Parametern, von denen pro Token rund 3,5 Milliarden
aktiv sind. Die [Modellkarte](https://huggingface.co/Aleph-Alpha/Kolibri-1)
beschreibt unter anderem synthetische Umformulierungen mit Gemma und Mistral.
Die [Sovereign Models Scorecard von Here Be Dragons](https://huggingface.co/datasets/here-be-dragons-ai/sovereign-models-scorecard)
dokumentiert für das Post-Training vor allem GLM-5.2, GLM-5.3 und Qwen3.8-27B
als Datenlieferanten. Aleph Alpha beschreibt außerdem eigene Maßnahmen gegen
politischen Bias aus synthetischen Trainingsdaten.

**Apertus** entstand im Rahmen der Swiss AI Initiative von ETH Zürich und EPFL
mit dem Schweizer Supercomputing-Zentrum CSCS. Wir testen die 8B-Instruct-Variante
der ersten Generation von September 2025. Sie wurde von Grund auf trainiert;
Gewichte, Datenaufbereitung und Trainingsverfahren sind offen dokumentiert.
Auch hier kommen externe Modelle ins Spiel: Laut
[technischem Bericht](https://arxiv.org/html/2509.14233v1#S4.SS1.SSS4)
erzeugten Llama 3.1 8B, Llama 3.3 70B, Qwen 2.5 72B, Qwen 3 14B und Qwen 3 32B
Antworten für das Alignment. Bei kontroversen Themen orientiert sich dieses
an der Swiss AI Charter. Die Scorecard führt die spätere Generation Apertus 1.5
separat; deren Trainingsgeschichte ist nicht mit der hier getesteten Version
gleichzusetzen.

Die Herkunft der Tutormodelle allein belegt noch keinen übernommenen Bias.
Deshalb messen wir auch bei diesen europäischen Modellen das tatsächliche
Antwortverhalten im selben Test.

`alephalpha/kolibri-1-tl5` und `publicai/apertus-8b-instruct` erweitern den
Vergleich. Fragen, Rubrik, Temperatur und Tokenlimits stimmen mit den anderen
Läufen überein. Sie sind keine Kontrollmodelle für Aretes Training: Modellfamilien,
Größen und Serving unterscheiden sich. Die Proxy-Snapshots enthalten für diese
beiden Modelle keine verifizierte unveränderliche Gewichtsrevision.

### Kolibri

Auf **{k['n']} vollständigen Sprachpaaren** beträgt der Faktenscore
{num(k['en']['fact_mean'])} auf Englisch und {num(k['de']['fact_mean'])} auf Deutsch.
{ k['en']['propaganda_count']} englische und {k['de']['propaganda_count']} deutsche
Antworten tragen eine Propaganda-Markierung.

[[eval:kolibri]]

Dazu gehören viele Verweigerungen: {k['en']['refusal_count']} auf Englisch und
{k['de']['refusal_count']} auf Deutsch in genau diesen Paaren. Wenig markierte
Propaganda allein sagt deshalb wenig über den Nutzwert der Antworten aus.

### Apertus

Auf **{ap['n']} vollständigen Sprachpaaren** beträgt der Faktenscore
{num(ap['en']['fact_mean'])} auf Englisch und {num(ap['de']['fact_mean'])} auf Deutsch.
Der Judge markiert {ap['en']['propaganda_count']} englische und
{ap['de']['propaganda_count']} deutsche Antworten als Propaganda; als Verweigerung
markiert er {ap['en']['refusal_count']} beziehungsweise {ap['de']['refusal_count']}.

[[eval:apertus]]

## Alle vier Modelle auf denselben Fällen

Die Einzelkapitel verwenden die jeweils gültigen EN-DE-Paare. Für den direkten
Vergleich aller vier Modelle bleiben **{shared} identische Fragen** mit gültigen
Bewertungen in allen acht Bedingungen. {shared_exclusion}
Alle Werte hier wurden auf dieser gemeinsamen Fallmenge neu berechnet.

[[eval:all]]

Faktenscore, Propaganda-Markierungen und Verweigerungen stehen nebeneinander.
Eine einzelne Rangliste würde etwa den Unterschied zwischen einer sachlichen
Antwort und einer Verweigerung verdecken. Die gemeinsame Fallauswahl kontrolliert
die Fragezusammensetzung, nicht Modellgröße, Serving oder den Einfluss fehlender
Bewertungen.

## Grenzen des ersten Laufs

Es gibt einen Lauf pro Sprache und Modell, keine Streuung über Wiederholungen.
{remaining}
Übersetzungsfehler und sprachabhängige
Judge-Effekte bleiben möglich. Die Zahlen messen Referenzfakten und Marker dieser
Rubrik, keine allgemeine Wahrheit, politische Neutralität oder DACH-Rechtstauglichkeit.

## Daten ansehen und nachvollziehen

[[eval:huggingface]]

Die JSON-Downloads unter den Grafiken enthalten Vergleichswerte, exakte Fallmengen
und gültige Einzelfallbewertungen. Ein zusätzlicher Statusdownload führt alle
803 Fragen je Modell und Sprache mit Ausfällen und Ausschlussgründen auf.
Die separate Arete-Qwen-Auswertung verwendet
vier Bedingungen; der Gesamtvergleich verwendet acht. Fehlende und ungültige
Bewertungen werden nicht als Nullwerte ergänzt.

- [Datensatz auf Hugging Face](https://huggingface.co/datasets/here-be-dragons-ai/propaganda-eval-de)
- [Code, Prompts und dokumentierte Übersetzungsprüfung](https://github.com/here-be-dragons-ai/propaganda-eval-de)
- [Nous Research: Arete](https://nousresearch.com/arete)
- [OpenRouter: Qwen3.8-27B und Anbieter](https://openrouter.ai/qwen/qwen3.8-27b/providers)
'''
    start = body.index('## Was der Test misst')
    end = body.index('## Qwen auf Deutsch')
    methods = body[start:end]
    body = body[:start] + body[end:]
    pos = body.index('## Grenzen des ersten Laufs')
    body = body[:pos] + methods + body[pos:]
    body = body.replace('[[image]]', '[[image]]\n\n[[eval:headline]]')
    article.write_text('---\n'+'\n'.join(lines)+'\n---\n'+body)
    en = {'shared': shared, 'baseline_n': baseline['n']}
    for prefix, sample in [('q', q), ('a', a), ('k', k), ('ap', ap)]:
        en[prefix + '_n'] = sample['n']
        for lang in ('en', 'de'):
            key = prefix + '_' + lang
            en[key + '_fact'] = f"{sample[lang]['fact_mean']:.3f}"
            en[key + '_propaganda'] = sample[lang]['propaganda_count']
            en[key + '_propaganda_pct'] = f"{sample[lang]['propaganda_count'] / sample['n'] * 100:.3f}"
            en[key + '_refusal'] = sample[lang]['refusal_count']
    for lang in ('en', 'de'):
        en[lang + '_fact_gain'] = f"{g[lang]['fact_gain']:.3f}"
        en[lang + '_propaganda_reduction'] = f"{g[lang]['propaganda_reduction_percentage_points']:.3f}"
    en['fact_gain_difference'] = f"{diff['fact_gain']:.3f}"
    en['propaganda_reduction_difference'] = f"{diff['propaganda_reduction_percentage_points']:.3f}"
    en['primary_population'] = (
        'All **803 questions** have valid judgments for Arete and Qwen in both '
        'languages. No questions are excluded from this comparison.' if n == 803 else
        f'For the primary question, we retain only the **{n} questions** with valid '
        f'judgments for Arete and Qwen in both languages. This excludes {803-n} of the 803 questions.')
    en['shared_exclusion'] = ('No questions are excluded.' if shared == 803 else
                            'One question is excluded.' if shared == 802 else
                            f'{803-shared} questions are excluded.')
    en_failures = [f'{count} invalid {name} judgments' for name, count in invalid.items() if count]
    if truncated:
        en_failures.append(f'{truncated} ' + ('answer' if truncated == 1 else 'answers') +
                           ' left incomplete at the token limit')
    en['remaining'] = (
        'After retries, the following remain: ' + '; '.join(en_failures) +
        '. These cases are identified in the downloads and excluded from the common '
        'set, which could bias the results.' if en_failures else
        'All four models now have complete answers and valid judgments for all '
        '803 questions in both languages.')
    english = Template((ROOT / 'articles/arete-in-german.en.md.template').read_text()).substitute(en)
    (site / 'content/insights/arete-auf-deutsch.en.md').write_text(english)
    for name in ['comparison.json', 'cases.jsonl', 'status.jsonl']:
        (site/'public/insights/arete'/name).write_bytes((ROOT/'eval/article-comparison'/name).read_bytes())
    (site/'src/content/arete-comparison.json').write_bytes((ROOT/'eval/article-comparison/comparison.json').read_bytes())
    print('Updated article and downloads:',n,'primary cases;',shared,'all-model cases.')

if __name__ == '__main__': main()
