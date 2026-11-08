# Arete auf Deutsch: erster EN-DE-Vergleich

Ein Lauf mit 803 Fragen pro Sprache, abgeschlossen am 8. November 2026.
**775 identische Fälle haben in beiden Sprachen eine gültige Bewertung.**
Arete weist nach der ursprünglichen Bewertungsrubrik in beiden Sprachen selten
Propaganda auf; der Faktenscore liegt auf Deutsch niedriger.

## Ergebnisse

| Kennzahl, gleiche 775 Fälle | Englisch | Deutsch | Deutsch minus Englisch |
| --- | ---: | ---: | ---: |
| Mittlerer Faktenscore (0 bis 5) | 2,894 | 2,538 | −0,356 |
| Antworten mit mindestens einer Propaganda-Markierung | 7 | 5 | −2 |
| Anteil mit Propaganda-Markierung | 0,903 % | 0,645 % | −0,258 Prozentpunkte |

Sieben gegenüber fünf Ereignissen erlauben keine belastbare Aussage, dass Deutsch
besser abschneidet. Der Faktenscore misst die Abdeckung und den Widerspruch der
vorgegebenen Referenzfakten, keine allgemeine Wahrheitsquote.

| Fragetyp | Vollständige Paare | Faktenscore EN | Faktenscore DE |
| --- | ---: | ---: | ---: |
| closed exit | 16 | 3,438 | 2,250 |
| frame testing | 217 | 3,959 | 3,853 |
| named fact | 542 | 2,452 | 2,020 |

## Bezug zu Nous Research

[Nous Research](https://nousresearch.com/arete) berichtet für Arete mit deaktiviertem
Thinking einen englischen Faktenscore von 2,98 und 0,9 % Propaganda. Für das
Ausgangsmodell Qwen3.8-27B nennt Nous 2,32 und 22 %. Diese Werte stammen aus fünf
Läufen mit jeweils 803 Fragen. Unser englischer Lauf liegt mit 2,89 und 0,90 % in
einer ähnlichen Größenordnung. Er ist keine exakte Replikation: Wir verwenden
nur einen Lauf und werten primär die 775 vollständig bewerteten Sprachpaare aus.

**Ein passender eigener Qwen-Lauf fehlt.** Wir haben deshalb noch nicht gezeigt,
ob der von Nous gemessene Alignment-Gewinn gegenüber Qwen auch auf Deutsch gilt.
Dafür müssen Arete und Qwen unter denselben Bedingungen in beiden Sprachen
verglichen werden. Wir haben kein Modell trainiert oder nachtrainiert.

## Methode

- Modell: `NousResearch/Arete-27B`, Revision
  `108f0afbdcfaa1ceeda4a635004304dfff6d4da2`, Basis `Qwen/Qwen3.8-27B`.
- 803 englische Originalfragen und ihre eingefrorenen deutschen Übersetzungen;
  Englisch und Deutsch alternieren je Item. Keine Anpassung der politischen Fälle
  an Deutschland, Österreich oder die Schweiz.
- Eine RTX PRO 6000 mit 96 GB, BF16, vLLM 0.32.0, 65.536 Token Kontext.
  Containerdigest und Generierungsparameter stehen im [Manifest](manifest.json).
- Temperatur 0, maximal 32.768 Ausgabetoken, Thinking explizit deaktiviert.
  Eine Nutzernachricht, keine zusätzliche Systemnachricht für Arete.
- Judge: `x-ai/grok-4.7`, Temperatur 0, maximal 4.096 Ausgabetoken.
  Die [ursprüngliche englische Rubrik](judge.md), englische Originalfragen,
  Referenzfakten und Propaganda-Marker bleiben für beide Antwortsprachen gleich.
- Zusätzliche deterministische Validierung prüft Faktenzuordnung, Score-Konsistenz
  und Belegzitate. Ungültige Bewertungen werden nicht als gültige Nullwerte behandelt.

Von 1.606 geplanten Antworten wurden 1.597 erfolgreich erzeugt. Neun Anfragen
scheiterten technisch. Von 1.597 Bewertungen sind 1.574 gültig; 23 sind ungültig:
18 inkonsistente Faktenscores, vier ungültige Belegzitate und eine fehlerhafte
Partition der Referenzfakten. Zusammen betreffen die Ausfälle 28 Sprachpaare.
Der Bericht enthält zusätzlich eine ausdrücklich als solche bezeichnete
Nullimputation über alle 803 Fälle; sie ist nicht die primäre Auswertung.

## Daten und Reproduktion

- [Antworten](release/answers.jsonl): letzte gespeicherte Antwortversuche mit
  Anfragen, Parametern, Status, Zeitstempeln und Modellantworten.
- [Bewertungen](release/grades.jsonl): letzte gespeicherte Judge-Versuche,
  einschließlich ungültiger Bewertungen und Fehlerstatus.
- [Paare](release/pairs.jsonl): alle 803 IDs mit Einschlussstatus und Einzelscores.
- [Bericht](report.json): Aggregate und Untergruppen; Kategorien können überlappen.
- [Prüfsummen der Exporte](release/sha256.json), [EN-Snapshot](en.jsonl),
  [DE-Snapshot](de.jsonl), [Adjudikationsmanifest](adjudication-manifest.json).

Die Exporte enthalten die finalen Versuche, keine Historie der Wiederholungen.
Doppelte Transportkopien der Anfrage werden weggelassen. Die Einzeldateien des
Laufs bleiben lokal erhalten. `python3 scripts/export_arete_release.py` erzeugt
und validiert die Exporte aus diesen Einzeldateien. Die veröffentlichten
`pairs.jsonl` lassen sich unabhängig auswerten, indem nur `included: true`
gewählt und die Scores bzw. `propaganda > 0` je Sprache gemittelt werden.

## Grenzen

Ein Lauf liefert keine Streuung zwischen Wiederholungen. Fehlende Paare können die
Schätzung verzerren. Die sprachübergreifende Zuverlässigkeit des Judges wurde nicht
unabhängig kalibriert. Übersetzung und gemischte menschliche/KI-Adjudikation sind
zusätzliche Fehlerquellen; Details stehen in der [Übersetzungsmethodik](../../METHOD.md).
Die Ergebnisse gelten für diese Fragen und diese Rubrik, nicht für politische
Neutralität insgesamt oder für rechtliche und kulturelle Eignung im DACH-Raum.

## Quellen

- [Nous: Arete](https://nousresearch.com/arete)
- [Gepinnte Modellkarte](https://huggingface.co/NousResearch/Arete-27B/blob/108f0afbdcfaa1ceeda4a635004304dfff6d4da2/README.md)
- [Ursprünglicher Datensatz](https://huggingface.co/datasets/NousResearch/Propaganda_Eval/tree/401223a2bfcdcd99d4650a83c4d20565db0e56b8)
