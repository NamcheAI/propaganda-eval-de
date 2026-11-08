# Nächster Lauf: Qwen als Kontrollbedingung

Status: autorisiert, wartet auf Wiederherstellung des Inference-Servers.
Noch keine Qwen-Antworten erzeugt und keine GPU gestartet.

## Eingefrorener Vergleich

- Modell: `Qwen/Qwen3.8-27B`, Hub-Revision
  `37561816e66b5b9153b1b64c10968c18c1e6f4a0` (am 8. November 2026 aufgelöst).
- Dieselben 803 Items aus `arete-01/en.jsonl` und `arete-01/de.jsonl`.
- BF16, vLLM 0.32.0 mit demselben Image-Digest und 65.536 Token Kontext.
- Eine RTX PRO 6000 mit 96 GB, maximal eine GPU-Replik. Erst bei erreichbarem
  Gateway und verfügbarem Judge starten. Keine parallel laufende Arete-Replik.
- Temperatur 0, Thinking explizit aus, 32.768 Ausgabetoken, nur die Nutzerfrage.
- Englische und deutsche Anfragen je Item abwechseln. Mit niedriger Parallelität
  beginnen, nach erfolgreichen vollständigen Antworten bis acht erhöhen.
- Derselbe Judge `x-ai/grok-4.7`, unverändertes `arete-01/judge.md`,
  Temperatur 0, 4.096 Ausgabetoken und dieselbe strikte Ausgabevalidierung.
- Eigener Snapshot `eval/qwen-01`; Arete-Ergebnisse nicht überschreiben.
  Die tatsächliche Gateway-Route vor dem Snapshot über den Models-Endpunkt
  verifizieren. Backend-Revision und Chat-Template ebenfalls nachweisen.
- Nach Abschluss Scale-to-zero zulassen und tatsächlich null laufende Repliken prüfen.

## Auswertung

Primär nur die Schnittmenge der Fälle mit gültigen Bewertungen in allen vier
Bedingungen verwenden: Arete EN, Arete DE, Qwen EN, Qwen DE. Die bisherigen
Arete-Aggregate dafür auf genau dieser Schnittmenge neu berechnen.

Für den Faktenscore:

`Gewinn_EN = Arete_EN − Qwen_EN`

`Gewinn_DE = Arete_DE − Qwen_DE`

`Transferdifferenz = Gewinn_DE − Gewinn_EN`

Für Propaganda eine Verbesserung als Verringerung berichten:

`Verringerung_EN = Qwen_EN − Arete_EN`

`Verringerung_DE = Qwen_DE − Arete_DE`

`Transferdifferenz = Verringerung_DE − Verringerung_EN`

Anteile als Prozent, Differenzen als Prozentpunkte ausgeben. Pro Bedingung
Nenner, Ereignisanzahl und technische/ungültige Ausfälle ausweisen. Zusätzlich
Ergebnisse nach Fragetyp und die aus beiden Modellen ausgeschlossenen IDs
veröffentlichen. Ein Lauf liefert weiterhin keine Streuung zwischen Wiederholungen.
Es bleibt ein automatisierter Judge; keine ungeprüfte Signifikanz- oder Kausalbehauptung.

## Wiederaufnahme

1. Gateway mit Timeout prüfen; bei 530/Netzwerkausfall keine GPU starten.
2. Mit dem Projekt-Key die Modellliste lesen, Grok-Minimaltest durchführen.
3. Vorhandene Verda-Konfiguration aus `work/arete-verda/` und die zugehörige
   Infrastruktur prüfen; nur die benötigte Qwen-Instanz mit maximal einer Replik bereitstellen.
4. Einzelfall in EN/DE prüfen, Snapshot schreiben, wiederaufnehmbaren
   `scripts/generate_parallel.py` und `scripts/grade_queue.py` verwenden.
5. Den oben beschriebenen Vier-Bedingungen-Vergleich exportieren, validieren und
   den bestehenden Ergebnisbericht sowie den Namche-Artikel aktualisieren.

Quelle des Ausgangsmodells:
[Arete-Modellkarte](https://huggingface.co/NousResearch/Arete-27B/blob/108f0afbdcfaa1ceeda4a635004304dfff6d4da2/README.md).
