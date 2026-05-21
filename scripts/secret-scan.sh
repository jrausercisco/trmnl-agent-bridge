#!/usr/bin/env bash
set -euo pipefail

root="${1:-.}"

scan_paths=(
  "$root/README.md"
  "$root/SECURITY.md"
  "$root/CONTRIBUTING.md"
  "$root/CODE_OF_CONDUCT.md"
  "$root/docs"
  "$root/examples"
  "$root/plugins"
  "$root/templates"
  "$root/src"
  "$root/schemas"
  "$root/scripts"
  "$root/.agents"
  "$root/.claude-plugin"
  "$root/.github"
  "$root/pyproject.toml"
)

existing_paths=()
for path in "${scan_paths[@]}"; do
  if [[ -e "$path" ]]; then
    existing_paths+=("$path")
  fi
done

patterns=(
  'TRMNL_WEBHOOK_URL[[:space:]]*=[[:space:]]*https?://'
  'https?://[^[:space:]"]*trmnl[^[:space:]"]*/api/custom_plugins/[A-Za-z0-9_-]{8,}'
  'BEGIN (RSA |OPENSSH |EC |DSA )?PRIVATE KEY'
  'xox[baprs]-[A-Za-z0-9-]{10,}'
  'gh[pousr]_[A-Za-z0-9_]{20,}'
  'sk-[A-Za-z0-9]{20,}'
  '/Users/'"jrauser"
  'END'"URANCE"
  'AM'"OS"
)

failed=0
for pattern in "${patterns[@]}"; do
  if rg -n --hidden --glob '!**/__pycache__/**' --glob '!**/*.pyc' --glob '!tests/**' "$pattern" "${existing_paths[@]}"; then
    failed=1
  fi
done

if [[ "$failed" -ne 0 ]]; then
  echo "secret-scan: potential private values or workspace references found" >&2
  exit 1
fi

echo "secret-scan: clean"
