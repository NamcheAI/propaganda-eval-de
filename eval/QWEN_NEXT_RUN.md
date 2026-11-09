# Qwen control run: completed

Generation in `eval/qwen-01` is complete with all 1,606 responses. Qwen ran through OpenRouter
and the Namche gateway. Thinking is disabled with `reasoning.enabled=false`; all responses
report zero reasoning tokens. Do not start a Qwen GPU or replace successful responses.

Configuration and checksums remain unchanged in the run manifest. Public provider metadata
is in `qwen-01/openrouter-model-metadata.json`; actual provider selection must be distinguished
from the endpoints listed in the catalog. The disabled Hetzner route is not an active second provider.

The primary Arete-Qwen comparison uses the intersection of all four language conditions.
The supplementary Apertus/Kolibri comparison uses eight. All targeted repairs and exports
are complete and have been independently recalculated. The primary comparison contains all
803 questions; the four-model comparison contains 802. One German Apertus response remains
incomplete at the token limit. Invalid or incomplete results are not scored as zeros.

[Protocol](PROTOCOL.md) | [Results report](article-comparison/README.md)

The article is published in [English](https://namche.ai/insights/arete-auf-deutsch?language=en)
and [German](https://namche.ai/insights/arete-auf-deutsch?language=de).
