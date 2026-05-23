# TRMNL Agent Bridge Launch Post

## Short Post

I published `trmnl-agent-bridge`, a local-first CLI and plugin bundle for sending compact agent/workflow status to a TRMNL Private Plugin webhook.

It is meant for "what needs attention now" signals from Codex, Claude Code, scripts, CI, cron jobs, or local automation. It is not a Claude usage dashboard and it does not scrape prompts, logs, session files, mail, calendar content, or private notes.

An agent can create a one-off webhook script; this repo packages the reusable safety and setup work around that script: schema validation, dry-run output, credential redaction, Keychain storage, local preview, smoke tests, and TRMNL recipe layouts.

Repo: https://github.com/jrausercisco/trmnl-agent-bridge

Quick check:

```bash
pipx install git+https://github.com/jrausercisco/trmnl-agent-bridge.git
trmnl-agent sample | trmnl-agent push --stdin --dry-run
```

What it includes:

- schema-validated `agent-status.v1` payloads
- TRMNL `merge_variables` webhook posting
- macOS Keychain support for webhook/device credentials
- dry-run, smoke-test, local preview, and optional current-screen verification
- Codex and Claude Code setup/publish/smoke-test skills
- TRMNL recipe packaging files for full, half-horizontal, half-vertical, and quadrant layouts
- GitHub Actions and cron examples for producing safe status payloads

I would value feedback on the setup flow and whether the `trmnl_plugin/` recipe package should be submitted or linked in the TRMNL Recipe Gallery.

## Longer Post

I published `trmnl-agent-bridge` as a small local-first bridge between local agent workflows and TRMNL.

The idea is simple: local agents and automations often know when something needs attention, but that signal stays buried in a terminal, browser tab, CI page, or chat thread. TRMNL is a good ambient surface for that kind of low-urgency state.

`trmnl-agent-bridge` gives those workflows a safe, repeatable path:

```bash
trmnl-agent sample | trmnl-agent push --stdin --dry-run
trmnl-agent sample | trmnl-agent push --stdin
```

The payload is intentionally small:

```json
{
  "schema_version": 1,
  "source": "codex",
  "title": "AGENT NOW",
  "state": "ACTION",
  "headline": "Review failed test run",
  "detail": "One workflow needs attention.",
  "next": "Last run completed 14:12",
  "signals": ["Tests: 1 failed", "PR: ready", "Agent: idle"],
  "health": "TRMNL webhook OK | payload 612 bytes",
  "updated": "14:13"
}
```

It wraps that under TRMNL `merge_variables`, validates the shape, keeps webhook/device credentials out of the repo, and supports dry-run/live smoke tests before publishing real workflow status.

This is deliberately not a Claude usage dashboard. It does not parse Claude session files or scrape local terminals. It is a generic "current agent status" bridge that can be used by Codex, Claude Code, shell scripts, CI, cron jobs, or other local producers.

The value is not that an agent could not build a custom version. The value is that the common plumbing is already documented, tested, and safer to reuse: payload validation, synthetic samples, local preview, credential redaction, Keychain storage, push-rate limits, recipe layouts, and setup/publish/smoke-test skills.

The repo also includes starting producer examples for GitHub Actions and cron, so users can adapt a working status emitter instead of beginning with a blank webhook script.

Repo: https://github.com/jrausercisco/trmnl-agent-bridge

Release: https://github.com/jrausercisco/trmnl-agent-bridge/releases/tag/v0.1.3

I would appreciate feedback on:

- first-run setup friction
- whether the payload fields are the right minimal contract
- whether the TRMNL recipe packaging should be submitted to or linked from the Recipe Gallery
- examples of local workflows that would make useful ambient TRMNL signals
