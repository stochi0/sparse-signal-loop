#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./lib/common.sh
source "${SCRIPT_DIR}/lib/common.sh"
# shellcheck source=./lib/uv.sh
source "${SCRIPT_DIR}/lib/uv.sh"

PRIME_POD_SKU="${PRIME_POD_SKU:-6ac679}"
REPO_DIR="${REPO_DIR:-${HOME}/sparse-signal-loop}"
SPARSE_SIGNAL_LOOP_REPO="${SPARSE_SIGNAL_LOOP_REPO:-}"

usage() {
  cat <<EOF
Prime pod helper (infra/bootstrap only). Phase runners are separate scripts:
  ./scripts/phase0/lbp.sh
  ./scripts/phase1/lbp.sh
  ./scripts/phase2/lbp.sh
  ./scripts/smoke.sh

Usage:
  $0 create
  $0 help-status
  $0 bootstrap

Environment:
  PRIME_POD_SKU            Availability id (default: ${PRIME_POD_SKU})
  REPO_DIR                 Clone path (default: ${REPO_DIR})
  SPARSE_SIGNAL_LOOP_REPO  Git URL used by bootstrap when REPO_DIR missing
EOF
}

cmd_create() {
  log "Creating pod with availability id ${PRIME_POD_SKU}"
  require_cmd prime
  prime pods create --id "${PRIME_POD_SKU}"
}

cmd_help_status() {
  cat <<'EOF'
Next steps (run on your local machine):

  prime pods list
  prime pods status <pod-id>
  prime pods ssh <pod-id>

If ssh says "Permission denied (publickey)":
  ./scripts/prime_ssh_key_upload.sh
  prime config set-ssh-key-path ~/.ssh/id_ed25519

Then create a NEW pod so the key is installed at provision time:
  prime pods create --id <sku>

When finished (stops billing):
  prime pods terminate <pod-id>
EOF
}

cmd_bootstrap() {
  # Intended to run *on the pod*.
  require_cmd sudo
  sudo apt-get update
  sudo apt-get install -y git curl build-essential

  ensure_uv

  if [[ -d "${REPO_DIR}/.git" ]]; then
    log "Repo already present at ${REPO_DIR}; pulling..."
    git -C "${REPO_DIR}" pull --ff-only || true
  else
    [[ -n "${SPARSE_SIGNAL_LOOP_REPO}" ]] || die "Set SPARSE_SIGNAL_LOOP_REPO to your git clone URL (or clone into REPO_DIR first)"
    git clone "${SPARSE_SIGNAL_LOOP_REPO}" "${REPO_DIR}"
  fi

  (cd "${REPO_DIR}" && uv sync)
  log "Bootstrap done."
  log "Next (on pod, inside repo):"
  log "  ./scripts/smoke.sh"
  log "  ./scripts/phase0/lbp.sh"
  log "  ./scripts/phase1/lbp.sh --smoke"
  log "  ./scripts/phase2/lbp.sh --smoke"
}

main() {
  local sub="${1:-help}"
  case "${sub}" in
    create) cmd_create ;;
    help-status) cmd_help_status ;;
    bootstrap) cmd_bootstrap ;;
    help|-h|--help) usage ;;
    *) die "unknown command: ${sub} (try: $0 help)" ;;
  esac
}

main "$@"

