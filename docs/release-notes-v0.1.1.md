# v0.1.1 Release Notes

## Summary

`v0.1.1` improves the first-run experience for users who install directly from GitHub and tightens credential redaction.

## Changes

- Added `trmnl-agent sample` to print a synthetic `agent-status.v1` payload without requiring a repository checkout.
- Added `--source` and `--state` options to the sample command for quick Codex, Claude Code, and generic payload checks.
- Updated README and setup docs to use `trmnl-agent sample | trmnl-agent push --stdin --dry-run` for checkout-free validation.
- Added TRMNL recipe packaging files under `trmnl_plugin/` for full, half-horizontal, half-vertical, and quadrant layout variants.
- Tightened credential redaction so status output reports credential values only as `<set>` or `<missing>`, without exposing prefixes or suffixes.
- Added tests for sample-payload generation, stdin dry-run publishing, stricter redaction, and release validation wiring.

## Install

```bash
pipx install --force git+https://github.com/jrausercisco/trmnl-agent-bridge.git
```

## Quick Check

```bash
trmnl-agent sample | trmnl-agent push --stdin --dry-run
trmnl-agent smoke-test
```

## Release Gate

Completed before publishing this release:

```bash
./scripts/validate-release.sh
trmnl-agent sample | trmnl-agent push --stdin
trmnl-agent smoke-test --push --fetch-screen --compare-screen --wait-seconds 30
```

The live gate used only synthetic data.

The webhook push returned HTTP 200 and current-screen fetch succeeded before and after the push. TRMNL returned a stable image hash inside the 30-second check window, so this patch release does not claim a visible display-change verification.
