# v0.1.3 Release Notes

## Summary

`v0.1.3` is a documentation and examples release that makes the bridge easier to adopt from real producers.

## Changes

- Added `examples/github-actions-agent-status.yml`, a manual GitHub Actions workflow that generates a schema-valid `agent-status.v1` payload and publishes through a `TRMNL_WEBHOOK_URL` repository secret.
- Added `examples/cron-agent-status.sh`, an executable cron/local-scheduler producer that reports a configured command's exit status without sending command output.
- Added `docs/producer-examples.md` with setup guidance for both examples and explicit status-only privacy boundaries.
- Updated README, value docs, and launch copy so the value proposition points to included producer examples.
- Shifted the roadmap from GitHub Actions and cron examples to additional producer examples for GitLab CI, Jenkins, Buildkite, launchd, and systemd timers.
- Added tests and release-validation checks for producer example presence, cron executability, safe webhook handling, and shell syntax.

## Install

```bash
pipx install --force git+https://github.com/jrausercisco/trmnl-agent-bridge.git@v0.1.3
```

## Quick Check

```bash
trmnl-agent sample | trmnl-agent push --stdin --dry-run
trmnl-agent preview --layout quadrant --merge-file examples/sample-payload.json
trmnl-agent smoke-test
```

## Producer Examples

```bash
./examples/cron-agent-status.sh --dry-run
```

For GitHub Actions, copy `examples/github-actions-agent-status.yml` into `.github/workflows/` and configure a `TRMNL_WEBHOOK_URL` repository or organization secret.

## Release Gate

Completed before publishing this release:

```bash
./scripts/validate-release.sh
trmnl-agent sample | trmnl-agent push --stdin
trmnl-agent smoke-test --push --fetch-screen --compare-screen --wait-seconds 30
```

The live gate used only synthetic data. No webhook URL, device ID, API token, response JSON, or screen image is included in the release.

The webhook push returned HTTP 200 and current-screen fetch succeeded before and after the push. TRMNL returned a stable image hash inside the 30-second check window, so this examples release does not claim a visible display-change verification.
