---
description: Run the TRMNL Agent Bridge smoke test in dry mode or live mode and summarize push and current-screen verification results.
---

# Smoke Test

Use this skill when the user asks to test, validate, verify, or smoke-test the TRMNL Agent Bridge from Claude Code.

## Dry Mode

Dry mode works without credentials and should be the default first check:

```bash
trmnl-agent smoke-test
```

From a local checkout:

```bash
PYTHONPATH=src python3 -m trmnl_agent_bridge.cli smoke-test
```

## Live Mode

Use live mode only when the user has configured a test TRMNL Private Plugin webhook and explicitly wants a live push:

```bash
trmnl-agent smoke-test --push
```

When TRMNL device API credentials are also configured, verify the rendered screen path:

```bash
trmnl-agent smoke-test --push --fetch-screen --compare-screen --wait-seconds 30
```

## Result Summary

Report:

- overall `ok`
- dry or live mode
- payload bytes and limit
- credential sources, never credential values
- push attempted and HTTP status when present
- current-screen fetch result when requested
- whether the before/after screen hash changed when comparison was requested

Do not echo webhook URLs, API tokens, device IDs, image URLs, or private payload bodies.
