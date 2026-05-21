# Codex Plugin

The Codex plugin bundle lives at `plugins/trmnl-agent-bridge` and is listed in `.agents/plugins/marketplace.json`.

## Skills

- `publish-status`: summarize the current Codex task into an `agent-status.v1` payload and publish or dry-run it with `trmnl-agent`.
- `setup`: guide local CLI installation, TRMNL Private Plugin setup, Keychain storage, and synthetic dry-run validation.
- `smoke-test`: run dry or live bridge validation and summarize the result without exposing secrets.

The skills are explicit by design. They do not add automatic hooks and they do not publish without a direct user request.

## Local Marketplace Test

To test marketplace discovery without touching the active Codex configuration:

```bash
tmp_base=$(mktemp -d /tmp/trmnl-agent-codex.XXXXXX)
mkdir -p "$tmp_base/home" "$tmp_base/codex"
HOME="$tmp_base/home" CODEX_HOME="$tmp_base/codex" codex plugin marketplace add /path/to/trmnl-agent-bridge
```

The expected result is that Codex adds the `trmnl-agent-bridge` marketplace from the local directory.

## Dry-Run The CLI Path

From the repository root:

```bash
PYTHONPATH=src python3 -m trmnl_agent_bridge.cli push --merge-file examples/sample-codex-status.json --dry-run
```

## Validate The Bundle

```bash
python3 -m json.tool plugins/trmnl-agent-bridge/.codex-plugin/plugin.json >/dev/null
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
PYTHONPATH=src python3 -m unittest discover -s tests
```

## Public Install Note

GitHub-hosted marketplace installation should be revalidated after the repo is public. Until then, the repo-local marketplace is the supported development surface.
