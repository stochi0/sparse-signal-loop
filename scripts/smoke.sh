#!/usr/bin/env bash
# Runs phase0/phase1/phase2 LBP smokes in parallel, logging to one directory.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./lib/common.sh
source "${SCRIPT_DIR}/lib/common.sh"

usage() {
  cat <<'EOF'
Parallel smoke for Phase 0/1/2 (LBP).

Usage:
  ./scripts/smoke.sh [--dry-run] [--log-dir DIR] [--dataset-start-index I]

Environment (optional):
  POLICY_MODEL, JUDGE_MODEL, DATASET_START_INDEX
  SMOKE_LOG_DIR (default base for auto log-dir)
EOF
}

DRY_RUN=0
LOG_DIR="${SMOKE_LOG_DIR:-}"
DATASET_START_INDEX="${DATASET_START_INDEX:-0}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --log-dir) LOG_DIR="${2:-}"; shift 2 ;;
    --dataset-start-index) DATASET_START_INDEX="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown option: $1 (try --help)" ;;
  esac
done

ROOT="$(repo_root)"
if [[ -z "${LOG_DIR}" ]]; then
  LOG_DIR="${ROOT}/outputs/smoke_logs/$(date -u +%Y%m%dT%H%M%SZ)"
fi
mkdir -p "${LOG_DIR}"

common_args=(--dataset-start-index "${DATASET_START_INDEX}")
if [[ "${DRY_RUN}" -eq 1 ]]; then
  common_args+=(--dry-run)
fi

pids=()
names=()

run_bg() {
  local name="$1"
  shift
  (
    set -euo pipefail
    "$@"
  ) >"${LOG_DIR}/${name}.log" 2>&1 &
  pids+=($!)
  names+=("${name}")
}

log "Smoke logs: ${LOG_DIR}"
log "  phase0-lbp → ${LOG_DIR}/phase0-lbp.log"
log "  phase1-lbp → ${LOG_DIR}/phase1-lbp.log"
log "  phase2-lbp → ${LOG_DIR}/phase2-lbp.log"

run_bg phase0-lbp "${SCRIPT_DIR}/phase0/lbp.sh" "${common_args[@]}" -n 1 -r 1
run_bg phase1-lbp "${SCRIPT_DIR}/phase1/lbp.sh" "${common_args[@]}" --smoke
run_bg phase2-lbp "${SCRIPT_DIR}/phase2/lbp.sh" "${common_args[@]}" --smoke

rc=0
for i in "${!pids[@]}"; do
  if ! wait "${pids[$i]}"; then
    log "FAIL: ${names[$i]} (see ${LOG_DIR}/${names[$i]}.log)"
    rc=1
  else
    log "OK:   ${names[$i]}"
  fi
done

exit "${rc}"

