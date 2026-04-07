#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./lib/common.sh
source "${SCRIPT_DIR}/lib/common.sh"

usage() {
  cat <<'EOF'
Upload an SSH *public* key to Prime so new pods accept `prime pods ssh`.

Usage:
  ./scripts/prime_ssh_key_upload.sh [path/to/key.pub]

Environment:
  PRIME_API_KEY (required; can be loaded from .env / ENV_FILE)
  PRIME_API_BASE_URL (default: https://api.primeintellect.ai)
  SSH_KEY_NAME (default: local-ed25519)
  ENV_FILE (optional dotenv path)
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

load_dotenv
require_cmd curl python3

PUB="${1:-${HOME}/.ssh/id_ed25519.pub}"
[[ -f "${PUB}" ]] || die "public key not found: ${PUB}"
[[ -n "${PRIME_API_KEY:-}" ]] || die "PRIME_API_KEY is unset (set it via .env, ENV_FILE=..., or export PRIME_API_KEY=...)"

BASE_URL="${PRIME_API_BASE_URL:-https://api.primeintellect.ai}"

BODY="$(python3 -c "
import json, os, pathlib, sys
p = pathlib.Path(sys.argv[1]).expanduser()
print(json.dumps({
  'name': os.environ.get('SSH_KEY_NAME', 'local-ed25519'),
  'publicKey': p.read_text().strip(),
}))
" "${PUB}")"

RESP="$(mktemp)"
trap 'rm -f "${RESP}"' EXIT

log "Uploading ${PUB} to ${BASE_URL}/api/v1/ssh_keys/ (name: ${SSH_KEY_NAME:-local-ed25519}) ..."
CODE="$(curl -sS -o "${RESP}" -w '%{http_code}' -X POST "${BASE_URL}/api/v1/ssh_keys/" \
  -H "Authorization: Bearer ${PRIME_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "${BODY}")"

cat "${RESP}"
printf '\n'

if [[ "${CODE}" != "200" && "${CODE}" != "201" ]]; then
  die "HTTP ${CODE}"
fi

log "OK. Ensure prime uses the matching private key:"
log "  prime config set-ssh-key-path ${PUB%.pub}"
log "If ssh still fails on an existing pod, terminate it and create a new one so the key is installed."

