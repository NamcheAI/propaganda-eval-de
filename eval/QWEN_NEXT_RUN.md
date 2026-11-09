# Qwen-Kontrolllauf

Die Generierung in `eval/qwen-01` ist mit allen 1.606 Antworten abgeschlossen.
Qwen wurde über OpenRouter und den Namche-Gateway ausgeführt. Thinking ist mit
`reasoning.enabled=false` ausgeschaltet; alle Antworten melden null Reasoning-Tokens.
Keine eigene Qwen-GPU starten und keine erfolgreichen Antworten ersetzen.

Konfiguration und Prüfsummen bleiben im Run-Manifest unverändert. Öffentliche
Anbieter-Metadaten stehen in `openrouter-model-metadata.json`; die tatsächliche
Anbieterwahl ist von den verfügbaren Katalog-Endpunkten zu unterscheiden.
Die deaktivierte Hetzner-Route ist kein aktiver zweiter Anbieter.

Der primäre Arete-Qwen-Vergleich verwendet die gemeinsame Menge aller vier
Sprachbedingungen. Der ergänzende Vergleich mit Apertus/Kolibri verwendet acht.
Alle gezielten Reparaturen und Exporte sind abgeschlossen und unabhängig nachgerechnet.
Der primäre Arete-Qwen-Vergleich enthält alle 803 Fragen, der Vier-Modell-Vergleich
802. Eine deutsche Apertus-Antwort bleibt am Tokenlimit unvollständig.
Ungültige oder unvollständige Ergebnisse werden nicht als Nullwerte gewertet.

[Protokoll](PROTOCOL.md) | [Ergebnisbericht](article-comparison/README.md)

Der Website-Artikel bleibt während der Wartung im offenen PR198.
Nicht mergen oder deployen.
