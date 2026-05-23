# Why TRMNL Agent Bridge Exists

`trmnl-agent-bridge` is useful because it turns a one-off agent-generated TRMNL experiment into a repeatable, safer, tested setup for local agent status.

An agent can create a custom TRMNL webhook script. The value here is that users do not have to rediscover the same practical details every time:

- which TRMNL Private Plugin strategy to choose
- how to paste raw markup instead of rendered Liquid text
- how to keep webhook URLs and device credentials out of committed files
- how to validate payload shape before posting
- how to keep payloads small enough for TRMNL
- how to dry-run before a live push
- how to verify the current-screen path when device credentials are available
- how to reuse full, half-horizontal, half-vertical, and quadrant layouts
- how to let Codex and Claude Code publish status without leaking prompts, logs, files, mail, calendar data, customer data, or secrets

The bridge is not meant to replace every custom dashboard. It is a safe starting point for the common part of many local-agent dashboards: publish one compact "what needs attention now" signal to TRMNL.

## Why Not Just Ask An Agent To Build One?

For a single private experiment, asking an agent to build a custom script may be enough.

For something reusable, the repeated work is not the initial webhook POST. The repeated work is the operational surface around it:

- stable payload contract
- synthetic first-run payloads
- local preview
- dry-run output
- webhook and device credential redaction
- macOS Keychain storage
- payload size checks
- push-rate limits
- release validation
- secret scanning
- setup docs
- TRMNL recipe packaging
- Codex and Claude Code skills with explicit safety rules

This project packages those details so a user can focus on the signal they want to display rather than rebuilding webhook plumbing and safety checks.

## Who Should Use It?

Use this bridge when you want a TRMNL screen to show:

- current Codex or Claude Code task status
- failed or passing local checks
- a waiting approval
- a stale queue
- a CI, cron, or workflow signal
- a homelab or local automation status
- a "come back to this later" reminder from a local agent

Do not use it when you need a dense analytics dashboard, account-usage accounting, or a hosted integration that pulls data directly from a SaaS API.

## How To Make It More Useful

The most useful improvements are producer examples and setup polish, not a bigger core payload. The repo now includes GitHub Actions and cron examples that emit `agent-status.v1` without sending logs or private content.

Good next additions:

- More producer examples for GitLab CI, Jenkins, Buildkite, launchd, and systemd timers.
- Disabled-by-default Codex and Claude hook examples for users who want automatic updates.
- More TRMNL template variants for different visual densities.
- A setup wizard that checks the webhook, template paste, and optional device API credentials in one command.
- Local preview improvements that more closely match TRMNL's framework rendering.
- Homebrew, PyPI, and packaged binary distribution.
- Windows Credential Manager and Linux Secret Service support.
- A recipe-gallery submission or link so users can install the display layout more easily.

The guiding principle should stay the same: make it easier to publish a small, safe, ambient status signal without turning the bridge into a private-data dashboard.
