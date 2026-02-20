#!/usr/bin/env bash
set -euo pipefail

_info() {
  echo "[langlearn-tts] $*"
}

_err() {
  echo "[langlearn-tts] Error: $*" >&2
  exit 1
}

_require_cmd() {
  command -v "$1" >/dev/null 2>&1 || _err "Missing required command: $1"
}

_check_python() {
  _require_cmd python3
  python3 - <<'PY' || exit 1
import sys
major, minor = sys.version_info[:2]
if (major, minor) < (3, 13):
    print("Python 3.13+ required.")
    raise SystemExit(1)
PY
}

_check_uv() {
  _require_cmd uv
}

_prompt_provider() {
  local provider
  read -r -p "Select provider [polly/openai/elevenlabs] (default: polly): " provider
  provider="${provider:-polly}"
  case "$provider" in
    polly|openai|elevenlabs)
      echo "$provider"
      ;;
    *)
      _err "Unknown provider: $provider"
      ;;
  esac
}

_prompt_key() {
  local label="$1"
  local var_name="$2"
  local key
  read -r -s -p "Enter $label: " key
  echo
  if [[ -z "$key" ]]; then
    _err "$label is required."
  fi
  export "$var_name"="$key"
}

_main() {
  _check_python
  _check_uv

  local provider
  provider="$(_prompt_provider)"

  case "$provider" in
    openai)
      _prompt_key "OPENAI_API_KEY" "OPENAI_API_KEY"
      ;;
    elevenlabs)
      _prompt_key "ELEVENLABS_API_KEY" "ELEVENLABS_API_KEY"
      ;;
  esac

  export LANGLEARN_TTS_PROVIDER="$provider"

  _info "Installing langlearn-tts via uv..."
  uv tool install punt-langlearn-tts

  _info "Configuring MCP server for Claude Desktop..."
  langlearn-tts install --provider "$provider"

  _info "Running doctor..."
  if ! langlearn-tts doctor; then
    _info "Doctor reported issues. Review the output above."
  fi

  _info "Done."
}

_main "$@"
