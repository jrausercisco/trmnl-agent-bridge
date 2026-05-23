#!/usr/bin/env bash
set -euo pipefail

python3 -m json.tool schemas/agent-status.v1.schema.json >/dev/null
python3 -m json.tool examples/sample-payload.json >/dev/null
python3 -m json.tool examples/sample-codex-status.json >/dev/null
python3 -m json.tool examples/sample-claude-status.json >/dev/null
python3 -m json.tool plugins/trmnl-agent-bridge/.codex-plugin/plugin.json >/dev/null
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool plugins/claude/trmnl-agent-bridge/.claude-plugin/plugin.json >/dev/null
python3 -m json.tool .claude-plugin/marketplace.json >/dev/null

test -f docs/payload-contract.md
test -f docs/release-process.md
test -f docs/release-notes-v0.1.0.md
test -f docs/release-notes-v0.1.1.md
test -f docs/release-notes-v0.1.2.md
test -f docs/release-notes-v0.1.3.md
test -f docs/launch-post.md
test -f docs/value.md
test -f docs/producer-examples.md
test -f docs/codex-plugin.md
test -f docs/claude-plugin.md
test -f docs/assets/synthetic-preview.svg
test -f examples/github-actions-agent-status.yml
test -f examples/cron-agent-status.sh
test -x examples/cron-agent-status.sh
test -f trmnl_plugin/plugin.yml
test -f trmnl_plugin/icon.svg
test -f trmnl_plugin/markup_full.html
test -f trmnl_plugin/markup_half_horizontal.html
test -f trmnl_plugin/markup_half_vertical.html
test -f trmnl_plugin/markup_quadrant.html

bash -n examples/cron-agent-status.sh

PYTHONPATH=src python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m trmnl_agent_bridge.cli sample | PYTHONPATH=src python3 -m trmnl_agent_bridge.cli push --stdin --dry-run >/dev/null
PYTHONPATH=src python3 -m trmnl_agent_bridge.cli preview --layout full --merge-file examples/sample-payload.json --output /tmp/trmnl-agent-full-preview.html >/dev/null
PYTHONPATH=src python3 -m trmnl_agent_bridge.cli preview --layout half-horizontal --merge-file examples/sample-payload.json --output /tmp/trmnl-agent-half-horizontal-preview.html >/dev/null
PYTHONPATH=src python3 -m trmnl_agent_bridge.cli preview --layout half-vertical --merge-file examples/sample-payload.json --output /tmp/trmnl-agent-half-vertical-preview.html >/dev/null
PYTHONPATH=src python3 -m trmnl_agent_bridge.cli preview --layout quadrant --merge-file examples/sample-payload.json --output /tmp/trmnl-agent-quadrant-preview.html >/dev/null
PYTHONPATH=src python3 -m trmnl_agent_bridge.cli push --merge-file examples/sample-payload.json --dry-run >/dev/null
PYTHONPATH=src python3 -m trmnl_agent_bridge.cli push --merge-file examples/sample-claude-status.json --dry-run >/dev/null
PYTHONPATH=src python3 -m trmnl_agent_bridge.cli smoke-test >/dev/null

if command -v claude >/dev/null 2>&1; then
  claude plugin validate . >/dev/null
  claude plugin validate ./plugins/claude/trmnl-agent-bridge >/dev/null
fi

./scripts/secret-scan.sh >/dev/null
