# Payload Contract

`trmnl-agent-bridge` publishes one compact JSON object to TRMNL under webhook `merge_variables`.

The contract is intentionally small so users can send useful status without exposing prompts, logs, private notes, email/calendar content, customer data, local file bodies, or secrets.

## Schema

The machine-readable schema lives at `schemas/agent-status.v1.schema.json`.

Required fields:

- `schema_version`: must be `1`.
- `source`: short producer name, such as `codex`, `claude`, `github-actions`, `cron`, or `homelab`.
- `state`: one of `CLEAR`, `WATCH`, `ACTION`, `BLOCKED`, or `FAIL`.
- `headline`: one display-sized status line.
- `detail`: one sentence of context.
- `updated`: local display time or timestamp.

Optional fields:

- `title`: short fixed screen title.
- `next`: next action or latest meaningful event.
- `signals`: up to four short status bullets.
- `health`: bridge or workflow health in one short line.
- `run_url`: link to a run, build, or task if safe to disclose.
- `repo`: repository name if safe to disclose.
- `branch`: branch name if safe to disclose.
- `task`: task label if safe to disclose.
- `expires_at`: optional stale-after timestamp.

Unknown fields are rejected by the CLI. This prevents accidental publication of raw logs or private source data.

## Example

```json
{
  "schema_version": 1,
  "source": "codex",
  "title": "AGENT NOW",
  "state": "ACTION",
  "headline": "Review failed test run",
  "detail": "One workflow needs attention.",
  "next": "Last run completed 14:12",
  "signals": [
    "Tests: 1 failed",
    "PR: ready",
    "Agent: idle"
  ],
  "health": "TRMNL webhook OK | payload 612 bytes",
  "updated": "14:13"
}
```

## State Guidance

- `CLEAR`: nothing needs attention.
- `WATCH`: something is in progress or worth tracking.
- `ACTION`: the user should look soon.
- `BLOCKED`: the workflow cannot continue without intervention.
- `FAIL`: a run, push, or verification step failed.

## Validation

Dry-run a payload:

```bash
trmnl-agent push --merge-file examples/sample-payload.json --dry-run
```

Dry-run from stdin:

```bash
cat examples/sample-claude-status.json | trmnl-agent push --stdin --dry-run
```

The dry-run output shows payload size, request size, state, headline, and the exact `merge_variables` body that would be sent.
