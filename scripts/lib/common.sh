#!/usr/bin/env bash
set -euo pipefail

log() { printf '%s\n' "$*" >&2; }
die() { log "error: $*"; exit 1; }

script_dir() {
  cd "$(dirname "${BASH_SOURCE[1]}")" && pwd
}

repo_root() {
  local d
  d="$(script_dir)"
  cd "${d}/../.." && pwd
}

require_cmd() {
  local c
  for c in "$@"; do
    command -v "${c}" >/dev/null 2>&1 || die "missing command: ${c}"
  done
}

load_dotenv() {
  # Loads the first existing file among:
  #   - $ENV_FILE (if set)
  #   - $REPO_DIR/.env (if REPO_DIR set and file exists)
  #   - repo-root/.env
  #
  # Exports variables from the file.
  local root f prime_api_key_before
  root="$(repo_root)"
  f=""
  prime_api_key_before="${PRIME_API_KEY:-}"

  if [[ -n "${ENV_FILE:-}" ]]; then
    [[ -f "${ENV_FILE}" ]] || die "ENV_FILE set but not found: ${ENV_FILE}"
    f="${ENV_FILE}"
  elif [[ -n "${REPO_DIR:-}" && -f "${REPO_DIR}/.env" ]]; then
    f="${REPO_DIR}/.env"
  elif [[ -f "${root}/.env" ]]; then
    f="${root}/.env"
  else
    return 0
  fi

  log "Loading environment from ${f}"
  # Make dotenv sourcing resilient:
  # - strips Windows CRLF
  # - supports lines like: export KEY=VALUE
  # - exports all sourced vars into the environment (set -a)
  require_cmd sed
  set -a
  # shellcheck disable=SC1090
  source <(sed -e 's/\r$//' -e 's/^[[:space:]]*export[[:space:]]\+//' "${f}")
  set +a

  # If PRIME_API_KEY was already exported in the local shell, prefer it over .env.
  # This avoids accidental override when .env has an empty/stale PRIME_API_KEY.
  if [[ -n "${prime_api_key_before}" ]]; then
    export PRIME_API_KEY="${prime_api_key_before}"
  fi
}

