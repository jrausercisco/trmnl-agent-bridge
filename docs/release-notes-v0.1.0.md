# v0.1.0 Release Notes

## Summary

`trmnl-agent-bridge` is a local-first CLI and agent plugin bundle for publishing compact agent status snapshots to TRMNL Private Plugin webhooks.

This first release includes:

- `trmnl-agent` CLI for payload validation, dry-run webhook body generation, live webhook push, preview rendering, credential status, Keychain storage, current-screen fetch, and smoke tests.
- `agent-status.v1` JSON schema and synthetic examples for generic, Codex, and Claude Code status payloads.
- TRMNL Liquid template for an 800x480 e-ink status screen.
- Codex plugin bundle with `publish-status`, `setup`, and `smoke-test` skills.
- Claude Code plugin bundle with matching skills and marketplace metadata.
- Public setup, payload, security, plugin, and release docs.
- Release hardening with CI, secret scanning, issue templates, contribution guidance, and security reporting docs.

## Install

```bash
pipx install git+https://github.com/jrausercisco/trmnl-agent-bridge.git
```

## Quick Check

```bash
trmnl-agent push --merge-file examples/sample-payload.json --dry-run
trmnl-agent preview --merge-file examples/sample-payload.json
trmnl-agent smoke-test
```

## Known Limits

- Live TRMNL push requires a user-created Private Plugin webhook.
- Device current-screen verification requires optional TRMNL device API credentials.
- Windows Credential Manager and Linux Secret Service are not implemented yet.
- GitHub Action and cron producer examples are planned post-launch.
- Automatic Codex or Claude hooks are intentionally not enabled in the MVP.

## Release Gate

Completed before publishing this release:

```bash
trmnl-agent push --merge-file examples/sample-payload.json
trmnl-agent smoke-test --push --fetch-screen --compare-screen --wait-seconds 30
```

The live gate used only synthetic data. The synthetic webhook push returned HTTP 200, current-screen metadata fetched successfully, and the before/after screen image hash changed.
