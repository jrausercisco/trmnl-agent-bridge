# Codex Automation Prompt Example

You are preparing a compact TRMNL status update for a local agent workflow.

Return a JSON object with these fields:

- `schema_version`: always `1`.
- `source`: use `codex`.
- `title`: short fixed title for the screen.
- `state`: one of `CLEAR`, `WATCH`, `ACTION`, `BLOCKED`, or `FAIL`.
- `headline`: the single most important current signal.
- `detail`: one sentence of context.
- `next`: the next action or last meaningful event.
- `signals`: up to four short status bullets.
- `health`: bridge or workflow health in one short line.
- `updated`: local display time.

Rules:

- Do not include secrets, tokens, webhook URLs, device IDs, private messages, customer names, or full logs.
- Keep every value short enough for an e-ink screen.
- Prefer the one thing a human should know next over a complete summary.
- If nothing needs attention, use `CLEAR`.
