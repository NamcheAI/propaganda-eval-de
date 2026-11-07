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
keine Vorschläge ohne menschliche Entscheidung. Widersprüchliche Feldentscheidungen und veraltete
Schreibstände werden abgewiesen. Bestehende Entscheidungen können im Filter „Entschieden“ bearbeitet werden.
Wenn sich zwei Entscheidungen zum selben Feld widersprechen, zunächst eine davon zurückstellen und
anschließend die gemeinsame Fassung abstimmen.

Diese erste Version läuft ausschließlich lokal. Mehrere Browser desselben Servers teilen dieselbe
Entscheidungsdatei; unabhängige Kopien sind kein gemeinsam synchronisierter Reviewdienst. Für verteilte
Expertenteams wäre ein gemeinsamer authentifizierter Dienst der nächste Schritt. GitHub Issues eignen
sich für übergreifende Terminologie- und Methodenfragen; die Einzelfallentscheidungen bleiben im Ledger.
Reviewernamen oder Kennungen in der Datei werden bei einer späteren Veröffentlichung sichtbar.

Nach Abschluss: `python3 scripts/finalize.py results`. Diese Prüfung verlangt zusätzlich den
vollständigen Modellreview und verweigert eine Finalisierung bei offenen oder widersprüchlichen Fällen.
