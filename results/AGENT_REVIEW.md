# Einzelprüfung der Minor-Befunde

Stand der Minor-Prüfung: 8. November 2026. Beauftragte KI-Adjudikation durch Codex.
Der abschließende Release-Status steht in [FINAL_REVIEW.md](FINAL_REVIEW.md).

## Umfang und Ergebnis

Geprüft wurden alle 344 zu Beginn offenen Minor-Befunde in 286 Items.
Die bereits gespeicherten 39 menschlichen Entscheidungen wurden unverändert erhalten.

| Entscheidung | Befunde |
| --- | ---: |
| Modellvorschlag übernommen (`accept`) | 137 |
| Eigene Korrektur (`modify`) | 85 |
| Befund verworfen, Übersetzung beibehalten (`reject`) | 121 |
| Zurückgestellt (`defer`) | 1 |

222 Entscheidungen ändern den Text in 221 unterschiedlichen Feldern von 187 Items.
Mehrere Befunde können dasselbe Feld betreffen. Die Zahlen sind keine Fehlerrate des Datensatzes.

## Vorgehen

Arbeitsauftrag: „für die minors - gehe fall für fall durch, mach eine kurze recherche und entscheide
dann, inkl. dokumentation der entscheidung“.

Jeder Befund wurde mit dem englischen Benchmark-Feld, der deutschen Fassung, dem Modellhinweis
und dem verfügbaren Quellenkontext geprüft. Maßstab ist Bedeutungstreue, insbesondere Akteur,
Modalität, Quantor, politische Rahmung und Fachbegriff. Reine stilistische Varianten erzwingen
keine Änderung. Der englische Benchmark bleibt maßgeblich, auch wenn ein zugrunde liegender
Artikel oder Gesetzestext ausführlicher ist. Die freigegebene deutsche Zahlenformatierung gilt weiter.

Die Recherche nutzte die verlinkten Originalquellen, amtliche Parallelfassungen, Fachquellen und
bei Sprachfragen etwa die [Duden-Datumsregel](https://www.duden.de/sprachwissen/rechtschreibregeln/datum).
PDFs wurden, soweit technisch möglich, mit `pdftotext` ausgelesen. Bei gesperrten oder nicht
auslesbaren Quellen wurden Suchauszüge beziehungsweise ergänzende Quellen herangezogen.
Ein erfolgreicher HTTP-Abruf allein gilt nicht als inhaltliche Bestätigung.

Für 239 Befunde lag ausgelesener Text der angegebenen Quelle vor, für 86 ein passender Suchauszug.
Bei 19 war die ursprüngliche Quelle nicht nutzbar; ergänzende Belege oder die Beschränkung der
Entscheidung auf den eindeutigen EN-DE-Wortlaut sind jeweils dokumentiert. Diese Kategorien
beschreiben den Quellenzugriff, nicht eine vollständige Überprüfung sämtlicher Tatsachen des Items.

Die Prüfung erfolgte im interaktiven Codex-Arbeitsablauf, nicht als weiterer standardisierter
API-Reviewlauf mit einem neuen festen Prompt. Die dokumentierten Astra- und Fable-Prompts sowie
ihre Rohantworten bleiben unverändert. Methodische Grundlagen und Grenzen stehen in
[METHOD.md](../METHOD.md#quellen); insbesondere ersetzt diese KI-Prüfung keine unabhängige,
qualifizierte menschliche MQM-Bewertung oder repräsentative Stichprobe.

## Nachweise und Arbeitsfassung

- [agent-decisions.jsonl](agent-decisions.jsonl): Entscheidung, Begründung, Belege, Zeitpunkt und KI-Rolle je Issue-ID.
- [agent-research.jsonl](agent-research.jsonl): EN-Feld, deutsche Fassung vor und nach der Prüfung, Quellenzugriff und Einschränkungen je Befund.
- [agent-review-manifest.json](agent-review-manifest.json): Umfang und Prüfsummen der verwendeten Artefakte.
- [working-translation.jsonl](working-translation.jsonl): Arbeitsfassung mit menschlichen Entscheidungen, KI-Entscheidungen und Zahlenregel.

Im lokalen Interface sind KI-Entscheidungen unter „Entschieden“ einsehbar und menschlich
überschreibbar. Zurückgestellte Befunde bleiben offen. Menschliche Entscheidungen haben Vorrang;
eine widersprechende spätere Feldentscheidung macht betroffene KI-Entscheidungen erneut prüfpflichtig.

## Abschließende Entscheidung

**Fall 0548, Prompt:** „camps, exits, birth rates“. Die Recherche klärt nicht zuverlässig, ob
„exits“ Entlassungen aus den Lagern oder Ausreisen aus China bezeichnet. Die beauftragte
Schlussadjudikation entscheidet auf **Entlassungen**, gestützt auf Internierungs- und Lagerkontext
sowie den Referenzfakt zur Freilassung politischer Gefangener. Die Restunsicherheit bleibt dokumentiert.
Alle weiteren Hinweise sind ebenfalls entschieden; die finale Fassung enthält keine offenen Prüfpunkte.
