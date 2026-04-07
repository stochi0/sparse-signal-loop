#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./common.sh
source "${SCRIPT_DIR}/common.sh"

ensure_uv() {
  if command -v uv >/dev/null 2>&1; then
    return 0
  fi
  require_cmd curl
  log "uv not found; installing..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # shellcheck disable=SC1091
  [[ -f "${HOME}/.local/bin/env" ]] && source "${HOME}/.local/bin/env"
  export PATH="${HOME}/.local/bin:${PATH}"
  command -v uv >/dev/null 2>&1 || die "uv not found after install; add ~/.local/bin to PATH (or re-login)"
}

uv_sync_repo() {
  local root
  root="$(repo_root)"
  ensure_uv
  (cd "${root}" && uv sync)
}

