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
- Includes TRMNL recipe packaging files for full, half, and quadrant layout variants.

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
trmnl-agent sample | trmnl-agent push --stdin --dry-run
```

The deprecated `trmnl-codex` alias is kept for early local experiments. New docs and examples use `trmnl-agent`.

## Quick Start

Validate the synthetic sample without sending anything:

```bash
trmnl-agent sample | trmnl-agent push --stdin --dry-run
```

From a local checkout, you can also validate the checked-in example payload:

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
3. Paste the raw contents of `templates/agent-status.liquid.html` into the TRMNL markup editor.
4. Save the plugin so TRMNL generates a webhook URL.
5. Store the webhook URL outside the repo:

```bash
trmnl-agent keychain-set --account TRMNL_WEBHOOK_URL
```

If you are copying from a terminal on macOS, this puts the raw markup on your clipboard:

```bash
pbcopy < templates/agent-status.liquid.html
```

Do not copy from a browser-rendered view of the HTML file; that strips the markup tags and leaves only inline Liquid text.

6. Push only synthetic data first:

```bash
trmnl-agent sample | trmnl-agent push --stdin
```

See `docs/private-plugin-setup.md` for the full checklist.

The canonical single-template setup uses `templates/agent-status.liquid.html`. The `trmnl_plugin/` directory contains the same full layout plus recipe packaging files for TRMNL Recipe Gallery style submission or manual setup across full, half vertical, half horizontal, and quadrant display sizes.

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
  trmnl_plugin/
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

- Add GitHub Action and cron examples.
- Add packaged binary releases.
- Add Homebrew and PyPI distribution paths.
- Add Windows Credential Manager and Linux Secret Service support.
- Consider optional Codex and Claude hook examples that remain disabled by default.

## Non-Goals

- This is not an official TRMNL, OpenAI, Codex, Anthropic, or Claude Code project.
- This is not a hosted service.
- This does not publish private knowledge-base, calendar, mail, or customer data.
- This does not add automatic Claude or Codex hooks in the MVP.

## License

MIT. See `LICENSE`.
