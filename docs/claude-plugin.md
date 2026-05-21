# Claude Code Plugin

The Claude Code plugin bundle lives at `plugins/claude/trmnl-agent-bridge` and is listed in `.claude-plugin/marketplace.json`.

## Skills

- `publish-status`: summarize the current Claude Code task into an `agent-status.v1` payload and publish or dry-run it with `trmnl-agent`.
- `setup`: guide local CLI installation, TRMNL Private Plugin setup, Keychain storage, and synthetic dry-run validation.
- `smoke-test`: run dry or live bridge validation and summarize the result without exposing secrets.

The MVP intentionally does not include Claude hooks. Publishing to TRMNL remains explicit so the plugin cannot accidentally leak prompts, logs, local files, webhook URLs, device IDs, or API tokens.

## Validate The Marketplace And Plugin

From the repository root:

```bash
claude plugin validate .
claude plugin validate ./plugins/claude/trmnl-agent-bridge
```

## Local Marketplace And Install Test

To test without touching the active Claude configuration:

```bash
tmp_home=$(mktemp -d /tmp/trmnl-agent-claude.XXXXXX)
HOME="$tmp_home" claude plugin marketplace add /path/to/trmnl-agent-bridge
HOME="$tmp_home" claude plugin marketplace list
HOME="$tmp_home" claude plugin install trmnl-agent-bridge@trmnl-agent-bridge --scope local
```

## Dry-Run The CLI Path

From the repository root:

```bash
PYTHONPATH=src python3 -m trmnl_agent_bridge.cli sample --source claude | PYTHONPATH=src python3 -m trmnl_agent_bridge.cli push --stdin --dry-run
PYTHONPATH=src python3 -m trmnl_agent_bridge.cli push --merge-file examples/sample-claude-status.json --dry-run
```

## Public Install Note

GitHub-hosted marketplace installation should be revalidated after the repo is public. Until then, the repo-local marketplace is the supported development surface.
