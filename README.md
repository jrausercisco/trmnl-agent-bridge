# trmnl-agent-bridge

Publish compact local agent status snapshots to TRMNL Private Plugin webhooks.

`trmnl-agent-bridge` is a local-first CLI and plugin bundle for sending calm status updates from Codex, Claude Code, scripts, CI, cron jobs, and other local automation to a TRMNL e-ink display. It does not run a hosted service and it does not need access to private prompts, logs, notes, mail, or calendar content.

## What It Does

- Validates a small `agent-status.v1` JSON payload.
- Wraps that payload under TRMNL webhook `merge_variables`.
- Pushes to a TRMNL Private Plugin webhook when explicitly requested.
- Stores webhook/device credentials through environment variables or macOS Keychain.
- Renders a local 800x480 HTML preview.
- Runs dry and live smoke tests.
- Ships Codex and Claude Code skills for setup, status publishing, and smoke tests.

## Install

From a local checkout:

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -e .
```

From GitHub after the repository is public:

```bash
pipx install git+https://github.com/jrausercisco/trmnl-agent-bridge.git
```

Check the CLI:

```bash
trmnl-agent status
```

The deprecated `trmnl-codex` alias is kept for early local experiments. New docs and examples use `trmnl-agent`.

## Quick Start

Validate the synthetic sample without sending anything:

```bash
trmnl-agent push --merge-file examples/sample-payload.json --dry-run
```

Render a local preview:

```bash
trmnl-agent preview --merge-file examples/sample-payload.json
```

Run the dry smoke test:

```bash
trmnl-agent smoke-test
```

## TRMNL Setup

1. Create a TRMNL Private Plugin.
2. Choose the webhook data strategy.
3. Paste `templates/agent-status.liquid.html` into the TRMNL markup editor.
4. Save the plugin so TRMNL generates a webhook URL.
5. Store the webhook URL outside the repo:

```bash
trmnl-agent keychain-set --account TRMNL_WEBHOOK_URL
```

6. Push only synthetic data first:

```bash
trmnl-agent push --merge-file examples/sample-payload.json
```

See `docs/private-plugin-setup.md` for the full checklist.

## Agent Plugins

This repo contains two agent plugin bundles:

- Codex: `plugins/trmnl-agent-bridge`, cataloged by `.agents/plugins/marketplace.json`.
- Claude Code: `plugins/claude/trmnl-agent-bridge`, cataloged by `.claude-plugin/marketplace.json`.

Each bundle contains three skills:

- `publish-status`: create and dry-run or publish a privacy-safe status payload.
- `setup`: guide CLI and TRMNL Private Plugin setup.
- `smoke-test`: validate the bridge without exposing secrets.

Codex local marketplace development:

```bash
codex plugin marketplace add /path/to/trmnl-agent-bridge
```

Claude Code local marketplace development:

```bash
claude plugin marketplace add /path/to/trmnl-agent-bridge
claude plugin install trmnl-agent-bridge@trmnl-agent-bridge --scope local
```

See `docs/codex-plugin.md` and `docs/claude-plugin.md`.

## Payload Contract

The public payload is intentionally small:

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

Allowed states are `CLEAR`, `WATCH`, `ACTION`, `BLOCKED`, and `FAIL`.

See `docs/payload-contract.md` and `schemas/agent-status.v1.schema.json`.

## Validation

Run the release validation script:

```bash
./scripts/validate-release.sh
```

It validates JSON files, runs unit tests, dry-runs the CLI, and runs Claude plugin validation when `claude` is installed.

## Security

Treat TRMNL webhook URLs, device IDs, and API tokens as secrets.

Do not commit:

- `.env` files
- webhook URLs
- device IDs
- API tokens
- response JSON from live pushes
- rendered screen images containing private data
- payloads copied from private workflows

The bridge should publish compact status, not raw prompts, transcripts, logs, email/calendar content, customer data, local file bodies, or private notes. See `docs/security.md`.

## Project Layout

```text
trmnl-agent-bridge/
  src/trmnl_agent_bridge/
  schemas/agent-status.v1.schema.json
  templates/agent-status.liquid.html
  examples/
  plugins/trmnl-agent-bridge/
  plugins/claude/trmnl-agent-bridge/
  .agents/plugins/marketplace.json
  .claude-plugin/marketplace.json
  docs/
  scripts/secret-scan.sh
  scripts/validate-release.sh
  .github/workflows/ci.yml
  tests/
```

## Roadmap

- Run a live synthetic TRMNL Private Plugin push before first public release.
- Publish the GitHub repository and tag `v0.1.0`.
- Confirm GitHub Actions CI passes on the hosted clean checkout.
- Verify GitHub-hosted Codex and Claude marketplace install flows.
- Add GitHub Action and cron examples.

## Non-Goals

- This is not an official TRMNL, OpenAI, Codex, Anthropic, or Claude Code project.
- This is not a hosted service.
- This does not publish private knowledge-base, calendar, mail, or customer data.
- This does not add automatic Claude or Codex hooks in the MVP.

## License

MIT. See `LICENSE`.
