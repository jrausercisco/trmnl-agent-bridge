# Release Process

This project requires a live synthetic TRMNL push and hosted CI checks before each public release.

## Pre-Release Checks

Run:

```bash
./scripts/validate-release.sh
```

This validates:

- JSON examples and manifests.
- Python unit tests.
- CLI dry-run push from sample payloads.
- CLI dry smoke test.
- Claude marketplace and plugin validation when `claude` is installed.

`validate-release.sh` runs the dedicated secret scan. You can also run it directly:

```bash
./scripts/secret-scan.sh
```

## Live Synthetic TRMNL Gate

Before tagging `v0.1.0`, run a live test against a TRMNL Private Plugin using only synthetic data:

```bash
trmnl-agent push --merge-file examples/sample-payload.json
```

When device API credentials are configured, also run:

```bash
trmnl-agent smoke-test --push --fetch-screen --compare-screen --wait-seconds 30
```

Do not save or commit response JSON or screen images unless they contain only synthetic data and have been reviewed.

## Public Launch Checklist

1. Confirm the repo contains no private paths, webhook URLs, API tokens, device IDs, response JSON, or private screenshots.
2. Confirm README, setup docs, payload contract, plugin docs, and security docs are current.
3. Confirm Codex and Claude local marketplace validation still passes.
4. Create the public GitHub repository.
5. Push the initial main branch.
6. Add GitHub topics: `trmnl`, `codex`, `claude-code`, `agent-skills`, `private-plugin`, `e-ink`, `webhooks`.
7. Tag `v0.1.0` only after validation and the live synthetic TRMNL gate pass.
8. Write release notes with install, setup, safety, and known-limitations sections.

## Known Pre-Launch Blockers

- None for `v0.1.0`.

## Completed Launch Checks

- Public GitHub repository created at `https://github.com/jrausercisco/trmnl-agent-bridge`.
- Initial `main` branch pushed.
- GitHub Actions CI passed on the hosted clean checkout.
- GitHub topics configured.
- GitHub-hosted Codex marketplace add verified from an isolated temporary Codex home.
- GitHub-hosted Claude marketplace add and plugin install verified from an isolated temporary home.
- Live synthetic TRMNL Private Plugin push returned HTTP 200.
- Live smoke test with current-screen fetch and screen comparison passed.
- `v0.1.0` release notes are in `docs/release-notes-v0.1.0.md`.
- `v0.1.0` tag and GitHub release published at `https://github.com/jrausercisco/trmnl-agent-bridge/releases/tag/v0.1.0`.
