#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/common.sh
source "${SCRIPT_DIR}/../lib/common.sh"
# shellcheck source=../lib/uv.sh
source "${SCRIPT_DIR}/../lib/uv.sh"

usage() {
  cat <<'EOF'
Run Phase 2 LBP.

Usage:
  ./scripts/phase2/lbp.sh [--dry-run] [--smoke] [--dataset-start-index I] [-m MODEL] [--judge-model MODEL]

Notes:
  --smoke forwards --smoke to ssl-phase2-lbp (tighter internal limits).

Environment (optional):
  POLICY_MODEL, JUDGE_MODEL, DATASET_START_INDEX
  PRIME_API_KEY (required unless --dry-run)
  ENV_FILE (optional dotenv path)
EOF
}

DRY_RUN=0
SMOKE=0
DATASET_START_INDEX="${DATASET_START_INDEX:-0}"
POLICY_MODEL="${POLICY_MODEL:-z-ai/glm-4.7}"
JUDGE_MODEL="${JUDGE_MODEL:-z-ai/glm-4.7-flash}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --smoke) SMOKE=1; shift ;;
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
  uv run ssl-phase2-lbp
  -m "${POLICY_MODEL}"
  --judge-model "${JUDGE_MODEL}"
  --dataset-start-index "${DATASET_START_INDEX}"
)
if [[ "${SMOKE}" -eq 1 ]]; then
  args+=(--smoke)
fi
if [[ "${DRY_RUN}" -eq 1 ]]; then
  args+=(--dry-run)
fi

"${args[@]}"

