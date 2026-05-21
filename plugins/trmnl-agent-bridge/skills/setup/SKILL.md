---
name: setup
description: Help a user install the trmnl-agent CLI, configure a TRMNL Private Plugin webhook, and verify a safe dry-run payload.
---

# Setup

Use this skill when the user asks to set up TRMNL Agent Bridge for Codex.

## Workflow

1. Verify the CLI is available:

```bash
trmnl-agent status
```

If the package is being used from a local checkout, run from the repository root:

```bash
PYTHONPATH=src python3 -m trmnl_agent_bridge.cli status
```

2. Have the user create a TRMNL Private Plugin with webhook-based updates.
3. Have the user paste `templates/agent-status.liquid.html` into the TRMNL plugin markup editor.
4. Store the webhook URL in an environment variable or macOS Keychain:

```bash
trmnl-agent keychain-set --account TRMNL_WEBHOOK_URL
```

5. Validate with a dry-run synthetic payload:

```bash
trmnl-agent push --merge-file examples/sample-payload.json --dry-run
```

6. Only after the dry run succeeds, push a synthetic payload:

```bash
trmnl-agent push --merge-file examples/sample-payload.json
```

## Safety

Webhook URLs, device IDs, and API tokens are secrets. Never put them in committed files, screenshots, logs, issue bodies, or chat output. Keep all setup validation on synthetic payloads until the user explicitly asks for a real status update.
