# Expertenprüfung

Start im Repository:

```sh
python3 scripts/review_ui.py
```

Interface: http://127.0.0.1:8765

1. Name oder stabile Kennung und Rolle beziehungsweise Qualifikation eintragen.
2. Einen Fall und darin einen Prüfpunkt auswählen. Original, Übersetzung und vollständigen Fallkontext lesen.
3. Vorschlag übernehmen, Übersetzung beibehalten, eigene Fassung eintragen oder zurückstellen.
4. Entscheidung begründen und bei Bedarf Belege ergänzen. Erst Speichern schreibt die Entscheidung.

Suche und Statusfilter helfen bei der Aufteilung; mit „Major / Fachfragen“ lassen sich wichtige Fälle
vorziehen. Ein Fall kann mehrere Prüfpunkte enthalten. Hinweise sind noch keine bestätigten Fehler.

Die Anwendung speichert atomar in `results/human-decisions.jsonl`, mit Reviewer, Rolle, Zeitpunkt,
Begründung, finalem Feldtext und Belegen. Zurückgestellte Punkte bleiben offen. Die Pipeline übernimmt
zusätzlich die ausdrücklich beauftragten KI-Einzelentscheidungen aus `results/agent-decisions.jsonl`.
Diese erscheinen mit der Kennzeichnung „KI-Einzelprüfung, keine menschliche Freigabe“.
Widersprüchliche menschliche Feldentscheidungen und veraltete
Schreibstände werden abgewiesen. Bestehende Entscheidungen können im Filter „Entschieden“ bearbeitet werden.
Wenn sich zwei Entscheidungen zum selben Feld widersprechen, zunächst eine davon zurückstellen und
anschließend die gemeinsame Fassung abstimmen.
Menschliche Entscheidungen überschreiben KI-Entscheidungen zum selben Prüfpunkt. Abweichende
menschliche Entscheidungen zu anderen Prüfpunkten desselben Feldes stellen die betroffenen
KI-Befunde zur erneuten Prüfung zurück. Beide ursprünglichen Entscheidungsdateien bleiben getrennt.

Diese erste Version läuft ausschließlich lokal. Mehrere Browser desselben Servers teilen dieselbe
Entscheidungsdatei; unabhängige Kopien sind kein gemeinsam synchronisierter Reviewdienst. Für verteilte
Expertenteams wäre ein gemeinsamer authentifizierter Dienst der nächste Schritt. GitHub Issues eignen
sich für übergreifende Terminologie- und Methodenfragen; die Einzelfallentscheidungen bleiben im Ledger.
Reviewernamen oder Kennungen in der Datei werden bei einer späteren Veröffentlichung sichtbar.

Die freigegebene Zahlenregel (`1,234` → `1.234`, `1.23` → `1,23`) gilt automatisch.
Das Interface zeigt den aktuellen Feldtext einschließlich gespeicherter Entscheidungen und Zahlenregel.
Reine Formatbefunde gelten als entschieden und erscheinen nicht mehr im Filter „Offen“.
Unter „Entschieden“ bleibt die Regelanwendung sichtbar; zusätzliche Bedeutungsfragen bleiben offen.
Die ursprünglichen Modelltexte und menschlichen Entscheidungseinträge bleiben für die Nachvollziehbarkeit erhalten.
`python3 scripts/apply_number_policy.py` exportiert die aktuelle Arbeitsfassung mit Änderungsnachweis.

Nach Abschluss: `python3 scripts/finalize.py results`. Diese Prüfung verlangt zusätzlich den
vollständigen Modellreview und verweigert eine Finalisierung bei offenen oder widersprüchlichen Fällen.

## Eigene Beobachtungen

„Alle 803 Fälle“ öffnet auch bisher unmarkierte Fälle; „Ohne Hinweis“ zeigt nur diese.
Unter „Eigenen Hinweis hinzufügen“ kann jedes übersetzte Feld ausgewählt werden. Name, Rolle
und Begründung sind erforderlich. Ein Vorschlag ist optional und noch keine Freigabe.

Eigene Hinweise werden getrennt in `results/human-findings.jsonl` gespeichert. Sie bleiben bei
einem erneuten Modellreview erhalten und müssen vor der Finalisierung ebenfalls entschieden sein.
Für Terminologiefragen können Suchbegriff und Regelvorschlag ergänzt werden. Die Fundstellen werden
mitgespeichert und können über die Suche einzeln geprüft werden. Es gibt keine globale Ersetzung.

Beispiel CCTV: Bei Überwachungsaufnahmen „Überwachungsvideo“ oder „Aufnahmen einer Überwachungskamera“;
beim chinesischen Fernsehsender „Videoausschnitt des Senders CCTV“. Maßgeblich bleibt der Kontext.
