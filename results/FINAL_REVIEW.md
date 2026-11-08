# Finale Übersetzung v1.0

Alle 803 Items sind übersetzt, modellgeprüft und adjudiziert. Alle 670 Prüfpunkte sind entschieden.
Die finale Fassung steht in [data/items.jsonl](../data/items.jsonl) und identisch in
[adjudicated.jsonl](adjudicated.jsonl). Der Datensatz ist für den ersten Eval-Lauf eingefroren.

## Entscheidungen

| Herkunft | Einträge |
| --- | ---: |
| Menschliche Entscheidungen | 39 |
| Beauftragte KI-Entscheidungen | 617 |
| Automatische Zahlenregel | 14 |

Zusätzlich korrigiert eine separat dokumentierte redaktionelle Entscheidung die Adjektivflexion
in Fall 1363: „einen sicherheitsrelevantes Verstoss“ wird zu „einen sicherheitsrelevanten Verstoss“.
Die ursprünglichen menschlichen Einträge bleiben unverändert; Schweizer Schreibweise und
inhaltliche Entscheidungen wurden beibehalten. Insgesamt unterscheiden sich 295 Textfelder
von der ursprünglichen Astra-Ausgabe.

Die Schlussprüfung entscheidet die zuletzt offenen 274 Hinweise: 251-mal Beibehalten und
23-mal eine eigene oder bereits entschiedene Fassung übernehmen. Dadurch ändern sich sieben
weitere Textfelder; ein zuvor entschiedener Befund desselben Feldes wird konsistent angeglichen.
Die Flexionskorrektur ist separat gezählt.

## Wesentliche Zweifelsentscheidungen

- **0548, exits:** „Entlassungen“, weil Internierung, Lager und der Referenzfakt zur Freilassung
  politischer Gefangener dafür sprechen. Die Quelle definiert das Wort nicht eindeutig.
- **f126, creditworthiness:** „Vertrauenswürdigkeit“ im Kontext redlicher Datenverarbeitung.
  [Amtliche Parallelfassung](https://en.spp.gov.cn/2021-12/29/c_948419.htm) und
  [DigiChina](https://digichina.stanford.edu/work/translation-personal-information-protection-law-of-the-peoples-republic-of-china-effective-nov-1-2021/)
  verwenden `good faith` beziehungsweise `sincerity`; eine finanzielle Bonitätsanforderung wäre irreführend.
- **1363, economic analysis:** Im Prompt bleibt „Wirtschaftsanalysen“ als Oberbegriff.
  Die menschliche Fassung „betriebswirtschaftliche und volkswirtschaftliche Forschung“ im
  Referenzfakt bleibt bestehen. Der Prompt wird dadurch nicht auf wissenschaftliche Forschung verengt.
- **Literalvergleiche:** `CO2`, ausgeschriebene Ordinalzahlen und HTML-Entitäten erzeugen
  technische Zahlenabweichungen, ohne die Sachzahlen zu verändern. Diese Hinweise sind einzeln entschieden.
- **Unvollständige oder widersprüchliche EN-Felder:** Fragmente und Quellwidersprüche bleiben
  erhalten; fehlende Titelteile und vermeintlich richtige Sachangaben werden nicht erfunden.

## Nachvollziehbarkeit und Grenzen

[final-review.jsonl](final-review.jsonl) enthält alle 274 Schlussentscheidungen mit EN-Feld,
Vorher/Nachher, Begründung, Belegen und Restunsicherheit. Die vollständigen aktuellen Entscheidungen
stehen in [agent-decisions.jsonl](agent-decisions.jsonl), die menschlichen Originaleinträge in
[human-decisions.jsonl](human-decisions.jsonl). Die Minor-Recherche bleibt separat dokumentiert.

Das ist eine gemischte menschliche und KI-Adjudikation nach ausdrücklicher Delegation der
Schlussentscheidungen. `human_validated` bleibt deshalb `false`; der Release-Status ist `final`.
Die gezielte Prüfung markierter Stellen ist keine repräsentative MQM-Fehlerratenmessung.
Ein finaler Datenstand bedeutet nicht, dass alle sprachlichen oder faktischen Unsicherheiten verschwunden sind.

[release-manifest.json](release-manifest.json) und [adjudication-manifest.json](adjudication-manifest.json)
dokumentieren Datenhash, Entscheidungsdateien und Anzahl der Änderungen. Der unveränderte
Modelloutput bleibt in [translated.jsonl](translated.jsonl).

Der vorbereitete Lauf [eval/main-01](../eval/main-01/) enthält 803 EN-DE-Paare mit eingefrorenem
Judge-Prompt und Konfiguration für Apertus und Kolibri. Er enthält noch keine generierten Antworten.
Dieser Vergleich ist eine Sprachbaseline; der Arete-gegen-Qwen-Transfervergleich benötigt die
entsprechenden Modellrouten und eine eigene Laufkonfiguration.
