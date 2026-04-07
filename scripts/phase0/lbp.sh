#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/common.sh
source "${SCRIPT_DIR}/../lib/common.sh"
# shellcheck source=../lib/uv.sh
source "${SCRIPT_DIR}/../lib/uv.sh"

usage() {
  cat <<'EOF'
Run Phase 0 LBP.

Usage:
  ./scripts/phase0/lbp.sh [--dry-run] [-n NUM] [-r ROLLOUTS] [--dataset-start-index I] [-m MODEL] [--judge-model MODEL]

Environment (optional):
  POLICY_MODEL, JUDGE_MODEL, NUM_EXAMPLES, ROLLOUTS, DATASET_START_INDEX
  PRIME_API_KEY (required unless --dry-run)
  ENV_FILE (optional dotenv path)
EOF
}

DRY_RUN=0
NUM_EXAMPLES="${NUM_EXAMPLES:-4}"
ROLLOUTS="${ROLLOUTS:-1}"
DATASET_START_INDEX="${DATASET_START_INDEX:-0}"
POLICY_MODEL="${POLICY_MODEL:-z-ai/glm-4.7}"
JUDGE_MODEL="${JUDGE_MODEL:-z-ai/glm-4.7-flash}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    -n) NUM_EXAMPLES="${2:-}"; shift 2 ;;
    -r) ROLLOUTS="${2:-}"; shift 2 ;;
    --dataset-start-index) DATASET_START_INDEX="${2:-}"; shift 2 ;;
    -m) POLICY_MODEL="${2:-}"; shift 2 ;;
    --judge-model) JUDGE_MODEL="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown option: $1 (try --help)" ;;
  esac
done

load_dotenv

ROOT="$(repo_root)"
cd "${ROOT}"

if [[ "${DRY_RUN}" -eq 0 && -z "${PRIME_API_KEY:-}" ]]; then
  die "PRIME_API_KEY is unset (set it via .env, ENV_FILE=..., or export PRIME_API_KEY=...). Use --dry-run to skip API calls."
fi

uv_sync_repo

args=(
  uv run ssl-phase0-lbp
  -m "${POLICY_MODEL}"
  --judge-model "${JUDGE_MODEL}"
  -n "${NUM_EXAMPLES}"
  --dataset-start-index "${DATASET_START_INDEX}"
  -r "${ROLLOUTS}"
)
if [[ "${DRY_RUN}" -eq 1 ]]; then
  args+=(--dry-run)
fi

"${args[@]}"

