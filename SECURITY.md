# Security Policy

`trmnl-agent-bridge` publishes small local status payloads to TRMNL Private Plugin webhooks. Webhook URLs, device IDs, API tokens, response JSON, screen images, and payloads copied from private workflows are sensitive.

## Reporting Security Issues

Use GitHub private security advisories when the repository is public:

```text
https://github.com/jrausercisco/trmnl-agent-bridge/security/advisories/new
```

Do not open public issues or pull requests containing credentials, private payloads, rendered screen images with private data, live response JSON, raw prompts, logs, email/calendar content, customer data, or local file bodies.

## Supported Versions

No public release has been tagged yet. Until `v0.1.0`, security fixes land on `main`.

## Project Security Model

- No hosted relay.
- No telemetry.
- No credentials committed to repo files.
- No automatic Codex or Claude Code publishing hooks in the MVP.
- Explicit pushes only.
- Compact status payloads only.

For the detailed security model and repository hygiene checklist, see `docs/security.md`.
