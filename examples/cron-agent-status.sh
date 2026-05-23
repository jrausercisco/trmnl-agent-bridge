#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: cron-agent-status.sh [--dry-run|--push]

Runs a small local check and publishes only the check result to TRMNL.

Environment:
  TRMNL_AGENT_CHECK_COMMAND  Shell command to run. Default: trmnl-agent status >/dev/null
  TRMNL_AGENT_CHECK_NAME     Short label shown on TRMNL. Default: Local agent check
  TRMNL_AGENT_SOURCE         Payload source label. Default: cron

Examples:
  ./examples/cron-agent-status.sh --dry-run
  TRMNL_AGENT_CHECK_COMMAND='make test >/dev/null' ./examples/cron-agent-status.sh --push
USAGE
}

mode="${1:---dry-run}"
if [[ "$mode" != "--dry-run" && "$mode" != "--push" ]]; then
  usage >&2
  exit 2
fi

if ! command -v trmnl-agent >/dev/null 2>&1; then
  echo "trmnl-agent is not installed or is not on PATH." >&2
  exit 127
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is not installed or is not on PATH." >&2
  exit 127
fi

tmp_payload="$(mktemp)"
trap 'rm -f "$tmp_payload"' EXIT

check_name="${TRMNL_AGENT_CHECK_NAME:-Local agent check}"
check_command="${TRMNL_AGENT_CHECK_COMMAND:-trmnl-agent status >/dev/null}"
source_name="${TRMNL_AGENT_SOURCE:-cron}"

set +e
bash -lc "$check_command"
check_exit="$?"
set -e

if [[ "$check_exit" -eq 0 ]]; then
  state="CLEAR"
  headline="${check_name} passed"
  detail="The scheduled local check completed successfully."
  next_action="No action needed."
else
  state="ACTION"
  headline="${check_name} needs attention"
  detail="The scheduled local check exited with status ${check_exit}."
  next_action="Review the failing local command."
fi

TRMNL_SOURCE="$source_name" \
TRMNL_STATE="$state" \
TRMNL_HEADLINE="$headline" \
TRMNL_DETAIL="$detail" \
TRMNL_NEXT="$next_action" \
TRMNL_CHECK_NAME="$check_name" \
TRMNL_CHECK_EXIT="$check_exit" \
TRMNL_MODE="$mode" \
python3 - <<'PY' > "$tmp_payload"
import datetime as dt
import json
import os


def clamp(value, limit):
    text = " ".join(str(value or "").split())
    return text[:limit]


payload = {
    "schema_version": 1,
    "source": clamp(os.environ.get("TRMNL_SOURCE", "cron"), 40),
    "title": "AGENT NOW",
    "state": clamp(os.environ.get("TRMNL_STATE", "WATCH"), 20),
    "headline": clamp(os.environ.get("TRMNL_HEADLINE"), 100),
    "detail": clamp(os.environ.get("TRMNL_DETAIL"), 180),
    "next": clamp(os.environ.get("TRMNL_NEXT"), 120),
    "signals": [
        "Producer: cron",
        f"Check: {clamp(os.environ.get('TRMNL_CHECK_NAME'), 60)}",
        f"Exit: {clamp(os.environ.get('TRMNL_CHECK_EXIT'), 12)}",
        f"Mode: {clamp(os.environ.get('TRMNL_MODE'), 16)}",
    ],
    "health": "Cron producer generated a compact status payload.",
    "updated": dt.datetime.now(dt.timezone.utc).strftime("%H:%M UTC"),
}
print(json.dumps(payload, separators=(",", ":")))
PY

if [[ "$mode" == "--push" ]]; then
  trmnl-agent push --merge-file "$tmp_payload"
else
  trmnl-agent push --merge-file "$tmp_payload" --dry-run
fi
