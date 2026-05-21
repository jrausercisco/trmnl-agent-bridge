# v0.1.2 Release Notes

## Summary

`v0.1.2` finishes the pre-distribution polish for first-run setup, local layout previews, and public positioning.

## Changes

- Updated Codex and Claude Code setup skills to use the installed-user `trmnl-agent sample` flow instead of requiring `examples/sample-payload.json`.
- Made the setup skills explicit about choosing TRMNL's `Webhook` data strategy.
- Pointed recipe-style setup to the `trmnl_plugin/` full, half-horizontal, half-vertical, and quadrant templates.
- Added `trmnl-agent preview --layout` support for full, half-horizontal, half-vertical, and quadrant preview sizes.
- Added a synthetic demo image at `docs/assets/synthetic-preview.svg` for README and launch-post use.
- Added a README FAQ distinguishing the bridge from Claude usage dashboards and clarifying that the core bridge does not read prompts or local session files.
- Added tests and release-validation checks for the setup-skill guidance, demo asset, FAQ, and preview layout sizes.

## Install

```bash
pipx install --force git+https://github.com/jrausercisco/trmnl-agent-bridge.git
```

## Quick Check

```bash
trmnl-agent sample | trmnl-agent push --stdin --dry-run
trmnl-agent preview --layout quadrant --merge-file examples/sample-payload.json
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
