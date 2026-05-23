# Producer Examples

`trmnl-agent-bridge` accepts any producer that can write an `agent-status.v1` JSON payload. The examples in `examples/` show two common starting points: a manual GitHub Actions workflow and a local cron script.

These examples publish status, not logs. Keep prompts, terminal output, file bodies, issue bodies, customer data, tokens, and webhook URLs out of payloads.

## GitHub Actions

Use `examples/github-actions-agent-status.yml` when you want a repository workflow to send a compact TRMNL status.

Setup:

1. Add a repository or organization secret named `TRMNL_WEBHOOK_URL`.
2. Copy `examples/github-actions-agent-status.yml` into `.github/workflows/publish-trmnl-agent-status.yml`.
3. Run the workflow manually from the Actions tab.
4. Start with synthetic values, then adapt the payload fields to the workflow signal you want to display.

The example installs the published bridge, generates `trmnl-status.json`, validates it through `trmnl-agent push`, and posts it to the webhook from the secret. It does not send workflow logs.

## Cron Or Local Scheduler

Use `examples/cron-agent-status.sh` when you want a local scheduled check to publish one ambient status.

Run a dry check first:

```bash
./examples/cron-agent-status.sh --dry-run
```

Run a specific check:

```bash
TRMNL_AGENT_CHECK_COMMAND='make test >/dev/null' ./examples/cron-agent-status.sh --dry-run
```

Publish when ready:

```bash
TRMNL_AGENT_CHECK_COMMAND='make test >/dev/null' ./examples/cron-agent-status.sh --push
```

For cron, install the CLI in a path cron can see and store the webhook outside the script, such as macOS Keychain:

```bash
trmnl-agent keychain-set --account TRMNL_WEBHOOK_URL
```

Then add a scheduler entry similar to:

```cron
*/30 * * * * cd /path/to/project && TRMNL_AGENT_CHECK_COMMAND='make test >/dev/null' /path/to/trmnl-agent-bridge/examples/cron-agent-status.sh --push
```

The cron example records the command exit code only. It does not include command output in the TRMNL payload.
