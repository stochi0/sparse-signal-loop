#!/usr/bin/env bash
# Upload a local SSH *public* key to Prime so new pods accept `prime pods ssh`.
# Docs: https://docs.primeintellect.ai/api-reference/ssh-keys/upload-ssh-key
#
# Usage:
#   export PRIME_API_KEY=...   # or: source repo .env
#   ./scripts/prime_upload_ssh_pubkey.sh [path/to/key.pub]
#
# Optional: SSH_KEY_NAME=my-mac  (default: local-ed25519)
#
# After uploading, create a NEW pod (or reprovision) if the old VM was created
# before this key existed — keys are typically baked in at provision time.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [[ -f "${REPO_ROOT}/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${REPO_ROOT}/.env"
  set +a
fi

PUB="${1:-${HOME}/.ssh/id_ed25519.pub}"
[[ -f "${PUB}" ]] || {
  echo "error: public key not found: ${PUB}" >&2
  exit 1
}
[[ -n "${PRIME_API_KEY:-}" ]] || {
  echo "error: set PRIME_API_KEY (Prime API bearer token), e.g. from repo .env" >&2
  exit 1
}

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

echo "Uploading ${PUB} to ${BASE_URL}/api/v1/ssh_keys/ (name: ${SSH_KEY_NAME:-local-ed25519}) ..."
CODE="$(curl -sS -o "${RESP}" -w '%{http_code}' -X POST "${BASE_URL}/api/v1/ssh_keys/" \
  -H "Authorization: Bearer ${PRIME_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "${BODY}")"

cat "${RESP}"
echo ""
if [[ "${CODE}" != "200" && "${CODE}" != "201" ]]; then
  echo "error: HTTP ${CODE}" >&2
  exit 1
fi

echo "OK. Ensure prime uses the matching private key:"
echo "  prime config set-ssh-key-path ${PUB%.pub}"
echo "If ssh still fails on an existing pod, terminate it and create a new one so the key is installed."
