# Expert review interface

Start from the repository root:

```sh
python3 scripts/review_ui.py
```

Interface: http://127.0.0.1:8765. The interface labels are in German.

1. Enter a name or stable identifier and your role or qualifications.
2. Select a case and a review point. Read the original, translation and full case context.
3. Accept the proposal, keep the translation, enter your own wording or defer the decision.
4. Explain your decision and add evidence where needed. Only saving writes the decision.

Search and status filters help divide the work; “Major / Fachfragen” prioritizes major findings
and specialist questions. A case can contain several review points. Flags are not confirmed errors.

The application writes atomically to `results/human-decisions.jsonl`, recording reviewer, role,
time, rationale, final field text and evidence. Deferred points remain open. The pipeline also
incorporates explicitly commissioned AI decisions from `results/agent-decisions.jsonl`.
These carry the label “KI-Einzelprüfung, keine menschliche Freigabe” (case-by-case AI review,
not human approval). Conflicting human field decisions and stale writes are rejected.
Existing decisions can be edited under “Entschieden” (decided). If two decisions conflict on
the same field, first defer one, then agree on a shared final wording.
Human decisions override AI decisions on the same review point. Divergent human decisions
on other review points in the same field reopen the affected AI findings. The two original
decision files remain separate.

This version runs locally only. Multiple browsers connected to the same server share one
decision file; independent copies are not a synchronized review service. Distributed expert
teams would need a shared authenticated service. GitHub Issues suit cross-cutting terminology
and methodology questions; case decisions remain in the ledger. Reviewer names or identifiers
in the file become visible when published.

The approved number policy (`1,234` → `1.234`, `1.23` → `1,23`) applies automatically.
The interface shows current field text, including stored decisions and number formatting.
Formatting-only findings count as resolved and no longer appear under “Offen” (open).
Their policy application remains visible under “Entschieden”; additional questions about
meaning remain open. Original model text and human decision records are preserved for audit.
`python3 scripts/apply_number_policy.py` exports the current working translation with a change record.

When finished, run `python3 scripts/finalize.py results`. This also requires complete model
review and refuses finalization if cases remain open or conflicting.

## Adding observations

“Alle 803 Fälle” (all 803 cases) also opens previously unflagged cases; “Ohne Hinweis” shows
only unflagged cases. Under “Eigenen Hinweis hinzufügen” (add your own finding), select any
translated field. Name, role and rationale are required. A proposed correction is optional
and does not constitute approval.

User findings are stored separately in `results/human-findings.jsonl`. They survive repeated
model reviews and must also be resolved before finalization. For terminology questions,
you can add a search term and a proposed rule. Occurrences are saved and can be reviewed
individually through search. There is no global replacement.

CCTV example: for surveillance footage, use “Überwachungsvideo” or “Aufnahmen einer
Überwachungskamera”; for the Chinese broadcaster, “Videoausschnitt des Senders CCTV”.
The context determines the meaning.
