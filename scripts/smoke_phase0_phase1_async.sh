#!/usr/bin/env bash
# End-to-end smoke: Phase 0 / 1 / 2 LBP in parallel (same machine / pod).
#
#   From repo root (PRIME_API_KEY in .env or env for real runs):
#     ./scripts/smoke_phase0_phase1_async.sh
#   If `uv` is missing (fresh pod / git clone only), installs it like prime_pod_phase0_flow.sh, then `uv sync`.
#
#   Config only (no API calls):
#     ./scripts/smoke_phase0_phase1_async.sh --dry-run
#
#   Override models (defaults match prime_pod_phase0_flow.sh):
#     POLICY_MODEL=... JUDGE_MODEL=... ./scripts/smoke_phase0_phase1_async.sh
#
set -euo pipefail

die() {
  echo "error: $*" >&2
  exit 1
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

POLICY_MODEL="${POLICY_MODEL:-z-ai/glm-4.7}"
JUDGE_MODEL="${JUDGE_MODEL:-z-ai/glm-4.7-flash}"
DATASET_START_INDEX="${DATASET_START_INDEX:-0}"
LOG_DIR="${SMOKE_LOG_DIR:-}"

DRY_RUN=0
for arg in "$@"; do
  case "${arg}" in
    --dry-run) DRY_RUN=1 ;;
    -h | --help)
      sed -n '2,22p' "$0"
      exit 0
      ;;
    *)
      die "unknown option: ${arg} (try --help)"
      ;;
  esac
done

load_dotenv() {
  local f=""
  if [[ -n "${ENV_FILE:-}" && -f "${ENV_FILE}" ]]; then
    f="${ENV_FILE}"
  elif [[ -f "${REPO_ROOT}/.env" ]]; then
    f="${REPO_ROOT}/.env"
  else
    return 0
  fi
  echo "Loading environment from ${f}"
  set -a
  # shellcheck disable=SC1090
  source "${f}"
  set +a
}

if [[ "${DRY_RUN}" -eq 0 ]]; then
  load_dotenv
fi

cd "${REPO_ROOT}" || die "cannot cd to ${REPO_ROOT}"

ensure_uv() {
  if command -v uv >/dev/null 2>&1; then
    return 0
  fi
  echo "uv not found; installing (same as prime_pod_phase0_flow.sh bootstrap)..."
  command -v curl >/dev/null 2>&1 || die "install curl first: sudo apt-get update && sudo apt-get install -y curl"
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # shellcheck disable=SC1091
  [[ -f "${HOME}/.local/bin/env" ]] && source "${HOME}/.local/bin/env"
  export PATH="${HOME}/.local/bin:${PATH}"
  command -v uv >/dev/null 2>&1 || die "uv not found after install; add ~/.local/bin to PATH or re-login"
}

ensure_uv
echo "Syncing dependencies (uv sync)..."
uv sync

if [[ -z "${LOG_DIR}" ]]; then
  LOG_DIR="${REPO_ROOT}/outputs/smoke_logs/$(date -u +%Y%m%dT%H%M%SZ)"
fi
mkdir -p "${LOG_DIR}"

DRY_FLAG=()
if [[ "${DRY_RUN}" -eq 1 ]]; then
  DRY_FLAG=(--dry-run)
fi

# Phase 0 / 1: minimal 1×1. Phase 2: built-in --smoke (chat-first, tighter limits; see ssl-phase2-lbp --help).
phase0_cmd=(
  uv run ssl-phase0-lbp
  -m "${POLICY_MODEL}"
  --judge-model "${JUDGE_MODEL}"
  -n 1
  --dataset-start-index "${DATASET_START_INDEX}"
  -r 1
  "${DRY_FLAG[@]}"
)
phase1_cmd=(
  uv run ssl-phase1-lbp
  -m "${POLICY_MODEL}"
  --judge-model "${JUDGE_MODEL}"
  -n 1
  --dataset-start-index "${DATASET_START_INDEX}"
  -r 1
  "${DRY_FLAG[@]}"
)
phase2_cmd=(
  uv run ssl-phase2-lbp
  -m "${POLICY_MODEL}"
  --judge-model "${JUDGE_MODEL}"
  --dataset-start-index "${DATASET_START_INDEX}"
  --smoke
  "${DRY_FLAG[@]}"
)

smoke_pids=()
smoke_names=()

run_smoke_bg() {
  local name=$1
  shift
  (
    set -euo pipefail
    cd "${REPO_ROOT}"
    "$@"
  ) >"${LOG_DIR}/${name}.log" 2>&1 &
  smoke_pids+=($!)
  smoke_names+=("${name}")
}

echo "Smoke logs: ${LOG_DIR}"
echo "  phase0-lbp → ${LOG_DIR}/phase0-lbp.log"
echo "  phase1-lbp → ${LOG_DIR}/phase1-lbp.log"
echo "  phase2-lbp → ${LOG_DIR}/phase2-lbp.log"
if [[ "${DRY_RUN}" -eq 1 ]]; then
  echo "Mode: --dry-run (no API calls)"
else
  [[ -n "${PRIME_API_KEY:-}" ]] || echo "warning: PRIME_API_KEY is unset"
fi

run_smoke_bg phase0-lbp "${phase0_cmd[@]}"
run_smoke_bg phase1-lbp "${phase1_cmd[@]}"
run_smoke_bg phase2-lbp "${phase2_cmd[@]}"

rc=0
for i in "${!smoke_pids[@]}"; do
  pid="${smoke_pids[$i]}"
  name="${smoke_names[$i]}"
  if ! wait "${pid}"; then
    echo "FAIL: ${name} (see ${LOG_DIR}/${name}.log)" >&2
    rc=1
  else
    echo "OK:   ${name}"
  fi
done

exit "${rc}"
