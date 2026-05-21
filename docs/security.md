# Security

`trmnl-agent-bridge` is designed for local-first publishing to a TRMNL Private Plugin webhook. The bridge should never require a hosted relay.

## Secrets

Treat these values as secrets:

- TRMNL webhook URLs.
- Device IDs.
- API tokens.
- Response JSON from live pushes.
- Screenshots or current-screen images that contain private data.
- Payloads copied from private workflows.

Never commit those values to this repository.

## Payload Privacy

The bridge should push compact status, not raw agent logs.

Good payload fields:

- Current state.
- Short headline.
- One-sentence detail.
- Next action.
- A few short signals.
- Last update time.

Avoid:

- Full chat transcripts.
- Private notes.
- Customer data.
- Email or calendar content.
- Access tokens.
- Local filesystem paths.
- Device identifiers.

## Credential Handling

Preferred credential sources:

1. Explicit CLI argument for one-off local testing.
2. Environment variables for shell sessions.
3. macOS Keychain for durable local use.

The CLI redacts credential values in status output as `<set>` or `<missing>` and does not print credential prefixes or suffixes. Do not paste full credential values into bug reports, screenshots, comments, or logs.

## Repository Hygiene

Run these before public release or any sensitive PR:

```bash
./scripts/validate-release.sh
./scripts/secret-scan.sh
```

The secret scan looks for concrete webhook URLs, common token formats, private keys, and private workspace names or paths in public-facing project files.

## Screenshots

Do not commit rendered screen images unless they contain only synthetic data and have been reviewed. The safest default is to keep screenshots out of the repo until the release process explicitly requires them.
