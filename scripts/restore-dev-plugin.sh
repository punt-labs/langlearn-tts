#!/usr/bin/env bash
set -euo pipefail

# Restore dev plugin state on main after a release tag.

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLUGIN_JSON="${REPO_ROOT}/.claude-plugin/plugin.json"

# Restore plugin.json (and commands/ if it exists) from the commit before release prep
restore_paths=("$PLUGIN_JSON")
if [[ -d "${REPO_ROOT}/commands" ]]; then
  restore_paths+=("commands/")
fi

git -C "$REPO_ROOT" checkout HEAD~1 -- "${restore_paths[@]}"
git -C "$REPO_ROOT" add "${restore_paths[@]}"
git -C "$REPO_ROOT" commit --no-verify -m "chore: restore dev plugin state"
