# Contributing

Thanks for considering a contribution to `trmnl-agent-bridge`.

## What Fits

Good contributions keep the project local-first, privacy-safe, and useful on a small e-ink screen.

Examples:

- payload validation improvements
- safer credential handling
- clearer setup docs
- synthetic examples for Codex, Claude Code, CI, cron, or homelab workflows
- TRMNL template improvements that keep the display calm and legible

## What Does Not Fit

Please do not submit:

- real webhook URLs, device IDs, API tokens, response JSON, or screen captures with private data
- payload examples copied from private prompts, logs, notes, email, calendar, customer data, or local files
- hosted relay services or telemetry
- automatic agent hooks that publish status without explicit user action

## Local Checks

Before opening a pull request, run:

```bash
./scripts/validate-release.sh
./scripts/secret-scan.sh
```

If you change the Claude plugin, also run:

```bash
claude plugin validate .
claude plugin validate ./plugins/claude/trmnl-agent-bridge
```

## Pull Requests

Keep PRs focused. Include:

- what changed
- why it helps
- validation commands run
- any known limits or follow-up work

Use synthetic payloads in tests and screenshots.
