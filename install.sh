#!/bin/sh
# Install langlearn-tts — language learning TTS for Claude Code and Claude Desktop.
# Usage: curl -fsSL https://raw.githubusercontent.com/punt-labs/langlearn-tts/<SHA>/install.sh | sh
#
# Optional env vars:
#   LANGLEARN_TTS_PROVIDER   polly (default), openai, or elevenlabs
#   OPENAI_API_KEY           required if provider=openai
#   ELEVENLABS_API_KEY       required if provider=elevenlabs
set -eu

# --- Colors (disabled when not a terminal) ---
if [ -t 1 ]; then
  BOLD='\033[1m' GREEN='\033[32m' YELLOW='\033[33m' NC='\033[0m'
else
  BOLD='' GREEN='' YELLOW='' NC=''
fi

info() { printf '%b▶%b %s\n' "$BOLD" "$NC" "$1"; }
ok()   { printf '  %b✓%b %s\n' "$GREEN" "$NC" "$1"; }
warn() { printf '  %b!%b %s\n' "$YELLOW" "$NC" "$1"; }
fail() { printf '  %b✗%b %s\n' "$YELLOW" "$NC" "$1"; exit 1; }

# TODO: revert to "punt-langlearn-tts" once PyPI org prefix is approved
PACKAGE="punt-langlearn-tts@git+https://github.com/punt-labs/langlearn-tts.git"
PACKAGE_SHORT="punt-langlearn-tts"
BINARY="langlearn-tts"
PROVIDER="${LANGLEARN_TTS_PROVIDER:-polly}"

# --- Step 1: Python ---

info "Checking Python..."

if command -v python3 >/dev/null 2>&1; then
  PYTHON=python3
elif command -v python >/dev/null 2>&1; then
  PYTHON=python
else
  fail "Python not found. Install Python 3.13+ from https://python.org"
fi

PY_MAJOR=$("$PYTHON" -c 'import sys; print(sys.version_info.major)')
PY_MINOR=$("$PYTHON" -c 'import sys; print(sys.version_info.minor)')

if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 13 ]; }; then
  fail "Python ${PY_MAJOR}.${PY_MINOR} found, but 3.13+ is required"
fi

ok "Python ${PY_MAJOR}.${PY_MINOR}"

# --- Step 2: uv ---

info "Checking uv..."

if command -v uv >/dev/null 2>&1; then
  ok "uv already installed"
else
  info "Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  if [ -f "$HOME/.local/bin/env" ]; then
    # shellcheck source=/dev/null
    . "$HOME/.local/bin/env"
  elif [ -f "$HOME/.cargo/env" ]; then
    # shellcheck source=/dev/null
    . "$HOME/.cargo/env"
  fi
  export PATH="$HOME/.local/bin:$PATH"
  if ! command -v uv >/dev/null 2>&1; then
    fail "uv install succeeded but 'uv' not found on PATH. Restart your shell and re-run."
  fi
  ok "uv installed"
fi

# --- Step 3: punt-langlearn-tts ---

info "Installing $PACKAGE_SHORT..."

# --force: overwrites existing binary (may exist from old package name or prior install)
uv tool install --force "$PACKAGE" || fail "Failed to install $PACKAGE_SHORT"
ok "$PACKAGE_SHORT installed"

if ! command -v "$BINARY" >/dev/null 2>&1; then
  export PATH="$HOME/.local/bin:$PATH"
  if ! command -v "$BINARY" >/dev/null 2>&1; then
    fail "$PACKAGE_SHORT installed but '$BINARY' not found on PATH"
  fi
fi

ok "$BINARY $(command -v "$BINARY")"

# --- Step 4: langlearn-tts install (MCP registration) ---

info "Configuring MCP server (provider: $PROVIDER)..."
printf '\n'
"$BINARY" install --provider "$PROVIDER"
printf '\n'

# --- Step 5: langlearn-tts doctor ---

info "Verifying installation..."
printf '\n'
"$BINARY" doctor || true
printf '\n'

# --- Done ---

printf '%b%b%s is ready!%b\n\n' "$GREEN" "$BOLD" "$PACKAGE_SHORT" "$NC"
printf 'Provider: %s\n' "$PROVIDER"
printf 'To change provider: langlearn-tts install --provider <name>\n\n'
