---
description: Summarize the current Claude Code task into a privacy-safe TRMNL agent-status payload and publish or dry-run it with the trmnl-agent CLI. Use when asked to publish, show, send, update, or dry-run the current task status on TRMNL.
---

# Publish Status

Use this skill when the user asks Claude Code to publish, show, send, update, or dry-run the current task status on TRMNL.

## Requirements

- Use the `agent-status.v1` payload shape.
- Keep the payload short enough for an e-ink screen.
- Do not include prompts, transcripts, raw logs, file contents, customer names, email/calendar content, webhook URLs, device IDs, API tokens, local secrets, or private message bodies.
- Prefer `source: "claude"` for Claude Code-originated payloads.
- Use `trmnl-agent push --stdin --dry-run` for previews or when the user did not clearly ask for a live push.
- Use `trmnl-agent push --stdin` only when the user clearly asks to publish to TRMNL.

## Payload Shape

```json
{
  "schema_version": 1,
  "source": "claude",
  "title": "CLAUDE NOW",
  "state": "WATCH",
  "headline": "Short current signal",
  "detail": "One sentence of useful context.",
  "next": "Next action or latest meaningful event.",
  "signals": [
    "Tests: dry run",
    "Agent: active"
  ],
  "health": "Dry run OK",
  "updated": "HH:MM"
}
```

Allowed `state` values are `CLEAR`, `WATCH`, `ACTION`, `BLOCKED`, and `FAIL`.

## Workflow

1. Decide the payload state:
   - `CLEAR`: no attention needed.
   - `WATCH`: progress or background activity worth tracking.
   - `ACTION`: the user should look soon.
   - `BLOCKED`: Claude Code cannot proceed without input.
   - `FAIL`: a command, validation, push, or verification failed.
2. Create a compact JSON payload using only the allowed fields.
3. Inspect the JSON for secrets or private content before running the CLI.
4. Run the CLI:

```bash
trmnl-agent push --stdin --dry-run
```

For a live publish requested by the user:

```bash
trmnl-agent push --stdin
```

If `trmnl-agent` is not on `PATH` and the repository checkout is available, run from the repository root:

```bash
PYTHONPATH=src python3 -m trmnl_agent_bridge.cli push --stdin --dry-run
```

## Output

Summarize whether the command was a dry-run or live push, whether validation passed, the payload state/headline, and any missing credential or webhook issue. Do not echo secret values.
