#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./lib/common.sh
source "${SCRIPT_DIR}/lib/common.sh"
# shellcheck source=./lib/uv.sh
source "${SCRIPT_DIR}/lib/uv.sh"

usage() {
  cat <<'EOF'
Run a "serious" full matrix across both datasets and all phases:
  - LongBench-Pro: phase0, phase1, phase2
  - mini-SWE:      phase0, phase1, phase2

Usage:
  ./scripts/serious_run_all.sh [options]

Options:
  --dry-run                    Print phase commands and config only (no API calls)
  --log-dir DIR                Log output directory (default: outputs/serious_runs/<UTC>/logs)
  --run-root DIR               Base run directory (default: outputs/serious_runs/<UTC>/runs)
  --dataset-start-index I      Start index for both datasets (default: 0)
  --model MODEL                Policy model id (default: z-ai/glm-4.7)
  --judge-model MODEL          Judge model id (default: z-ai/glm-4.7-flash)
  --num-examples-lbp N         Examples per LBP phase (default: 120)
  --num-examples-mswe N        Examples per mini-SWE phase (default: 60)
  --rollouts R                 Rollouts per example (default: 1)
  --max-concurrent C           Max concurrent rollouts (default: 1)
  --num-workers W              Env server workers int|auto (default: auto)
  --mswe-dataset NAME          mini-SWE dataset name (default: PrimeIntellect/SWE-Bench-Verified-Quick)
  --mswe-max-turns N           mini-SWE turns per rollout (default: 120)
  --lbp-max-turns-chat N       LBP chat turns per rollout (default: 12)
  --lbp-max-turns-rlm N        LBP RLM turns per rollout (default: 36)
  --max-judge-submissions N    In-loop max incorrect submissions (default: 10)
  --allow-git                  Enable git operations in mini-SWE envs
  --no-phase1-slice            Disable phase1_slice for phase1/phase2 on both datasets
  --phase2-skill-max-chars N   Phase 2 skill soft cap (default: 8000)

LBP phase2 RLM sandbox tuning:
  --lbp-rlm-sandbox-cpu N              (default: 8)
  --lbp-rlm-sandbox-memory-gb N        (default: 16)
  --lbp-rlm-sandbox-disk-gb N          (default: 16)
  --lbp-rlm-sandbox-timeout-minutes N  (default: 120)
  --lbp-rlm-code-exec-timeout N        (default: 180)
  --lbp-rlm-sub-llm-max-turns N        (default: 8)

Environment:
  PRIME_API_KEY required unless --dry-run
  ENV_FILE optional dotenv override (same behavior as other scripts)
EOF
}

DRY_RUN=0
ALLOW_GIT=0
NO_PHASE1_SLICE=0

DATASET_START_INDEX="${DATASET_START_INDEX:-0}"
POLICY_MODEL="${POLICY_MODEL:-z-ai/glm-4.7}"
JUDGE_MODEL="${JUDGE_MODEL:-z-ai/glm-4.7-flash}"
NUM_EXAMPLES_LBP="${NUM_EXAMPLES_LBP:-120}"
NUM_EXAMPLES_MSWE="${NUM_EXAMPLES_MSWE:-60}"
ROLLOUTS="${ROLLOUTS:-1}"
MAX_CONCURRENT="${MAX_CONCURRENT:-1}"
NUM_WORKERS="${NUM_WORKERS:-auto}"
MSWE_DATASET="${MSWE_DATASET:-PrimeIntellect/SWE-Bench-Verified-Quick}"
MSWE_MAX_TURNS="${MSWE_MAX_TURNS:-120}"
LBP_MAX_TURNS_CHAT="${LBP_MAX_TURNS_CHAT:-12}"
LBP_MAX_TURNS_RLM="${LBP_MAX_TURNS_RLM:-36}"
MAX_JUDGE_SUBMISSIONS="${MAX_JUDGE_SUBMISSIONS:-10}"
PHASE2_SKILL_MAX_CHARS="${PHASE2_SKILL_MAX_CHARS:-8000}"

LBP_RLM_SANDBOX_CPU="${LBP_RLM_SANDBOX_CPU:-8}"
LBP_RLM_SANDBOX_MEMORY_GB="${LBP_RLM_SANDBOX_MEMORY_GB:-16}"
LBP_RLM_SANDBOX_DISK_GB="${LBP_RLM_SANDBOX_DISK_GB:-16}"
LBP_RLM_SANDBOX_TIMEOUT_MINUTES="${LBP_RLM_SANDBOX_TIMEOUT_MINUTES:-120}"
LBP_RLM_CODE_EXEC_TIMEOUT="${LBP_RLM_CODE_EXEC_TIMEOUT:-180}"
LBP_RLM_SUB_LLM_MAX_TURNS="${LBP_RLM_SUB_LLM_MAX_TURNS:-8}"

RUN_STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
ROOT="$(repo_root)"
RUN_BASE="${ROOT}/outputs/serious_runs/${RUN_STAMP}"
RUN_ROOT_BASE="${RUN_BASE}/runs"
LOG_DIR="${RUN_BASE}/logs"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --allow-git) ALLOW_GIT=1; shift ;;
    --no-phase1-slice) NO_PHASE1_SLICE=1; shift ;;
    --log-dir) LOG_DIR="${2:-}"; shift 2 ;;
    --run-root) RUN_ROOT_BASE="${2:-}"; shift 2 ;;
    --dataset-start-index) DATASET_START_INDEX="${2:-}"; shift 2 ;;
    --model) POLICY_MODEL="${2:-}"; shift 2 ;;
    --judge-model) JUDGE_MODEL="${2:-}"; shift 2 ;;
    --num-examples-lbp) NUM_EXAMPLES_LBP="${2:-}"; shift 2 ;;
    --num-examples-mswe) NUM_EXAMPLES_MSWE="${2:-}"; shift 2 ;;
    --rollouts) ROLLOUTS="${2:-}"; shift 2 ;;
    --max-concurrent) MAX_CONCURRENT="${2:-}"; shift 2 ;;
    --num-workers) NUM_WORKERS="${2:-}"; shift 2 ;;
    --mswe-dataset) MSWE_DATASET="${2:-}"; shift 2 ;;
    --mswe-max-turns) MSWE_MAX_TURNS="${2:-}"; shift 2 ;;
    --lbp-max-turns-chat) LBP_MAX_TURNS_CHAT="${2:-}"; shift 2 ;;
    --lbp-max-turns-rlm) LBP_MAX_TURNS_RLM="${2:-}"; shift 2 ;;
    --max-judge-submissions) MAX_JUDGE_SUBMISSIONS="${2:-}"; shift 2 ;;
    --phase2-skill-max-chars) PHASE2_SKILL_MAX_CHARS="${2:-}"; shift 2 ;;
    --lbp-rlm-sandbox-cpu) LBP_RLM_SANDBOX_CPU="${2:-}"; shift 2 ;;
    --lbp-rlm-sandbox-memory-gb) LBP_RLM_SANDBOX_MEMORY_GB="${2:-}"; shift 2 ;;
    --lbp-rlm-sandbox-disk-gb) LBP_RLM_SANDBOX_DISK_GB="${2:-}"; shift 2 ;;
    --lbp-rlm-sandbox-timeout-minutes) LBP_RLM_SANDBOX_TIMEOUT_MINUTES="${2:-}"; shift 2 ;;
    --lbp-rlm-code-exec-timeout) LBP_RLM_CODE_EXEC_TIMEOUT="${2:-}"; shift 2 ;;
    --lbp-rlm-sub-llm-max-turns) LBP_RLM_SUB_LLM_MAX_TURNS="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown option: $1 (try --help)" ;;
  esac
done

load_dotenv
cd "${ROOT}"

if [[ "${DRY_RUN}" -eq 0 && -z "${PRIME_API_KEY:-}" ]]; then
  die "PRIME_API_KEY is unset (set it via .env, ENV_FILE=..., or export PRIME_API_KEY=...). Use --dry-run to skip API calls."
fi

mkdir -p "${RUN_ROOT_BASE}" "${LOG_DIR}"
uv_sync_repo

phase1_slice_flag=()
if [[ "${NO_PHASE1_SLICE}" -eq 1 ]]; then
  phase1_slice_flag+=(--no-phase1-slice)
fi

allow_git_flag=()
if [[ "${ALLOW_GIT}" -eq 1 ]]; then
  allow_git_flag+=(--allow-git)
fi

dry_flag=()
if [[ "${DRY_RUN}" -eq 1 ]]; then
  dry_flag+=(--dry-run)
fi

run_phase() {
  local name="$1"
  shift
  log ""
  log "=== ${name} ==="
  log "Command: $*"
  "$@" 2>&1 | tee "${LOG_DIR}/${name}.log"
}

run_lbp_phase() {
  local phase="$1"
  local cmd="ssl-phase${phase}-lbp"
  local name="phase${phase}-lbp"
  local run_root="${RUN_ROOT_BASE}/phase${phase}/lbp"
  local args=(
    uv run "${cmd}"
    -m "${POLICY_MODEL}"
    --judge-model "${JUDGE_MODEL}"
    -n "${NUM_EXAMPLES_LBP}"
    -r "${ROLLOUTS}"
    -c "${MAX_CONCURRENT}"
    -w "${NUM_WORKERS}"
    --dataset-start-index "${DATASET_START_INDEX}"
    --max-turns-chat "${LBP_MAX_TURNS_CHAT}"
    --max-turns-rlm "${LBP_MAX_TURNS_RLM}"
    --max-judge-submissions "${MAX_JUDGE_SUBMISSIONS}"
    --run-root "${run_root}"
  )
  if [[ "${phase}" != "0" ]]; then
    if ((${#phase1_slice_flag[@]})); then
      args+=("${phase1_slice_flag[@]}")
    fi
  fi
  if [[ "${phase}" == "2" ]]; then
    args+=(
      --phase2-skill-max-chars "${PHASE2_SKILL_MAX_CHARS}"
      --rlm-sandbox-cpu "${LBP_RLM_SANDBOX_CPU}"
      --rlm-sandbox-memory-gb "${LBP_RLM_SANDBOX_MEMORY_GB}"
      --rlm-sandbox-disk-gb "${LBP_RLM_SANDBOX_DISK_GB}"
      --rlm-sandbox-timeout-minutes "${LBP_RLM_SANDBOX_TIMEOUT_MINUTES}"
      --rlm-code-exec-timeout "${LBP_RLM_CODE_EXEC_TIMEOUT}"
      --rlm-sub-llm-max-turns "${LBP_RLM_SUB_LLM_MAX_TURNS}"
    )
  fi
  if ((${#dry_flag[@]})); then
    args+=("${dry_flag[@]}")
  fi
  run_phase "${name}" "${args[@]}"
}

run_mswe_phase() {
  local phase="$1"
  local cmd="ssl-phase${phase}-msap"
  local name="phase${phase}-mini-swe"
  local run_root="${RUN_ROOT_BASE}/phase${phase}/mini_swe"
  local args=(
    uv run "${cmd}"
    -m "${POLICY_MODEL}"
    --judge-model "${JUDGE_MODEL}"
    --dataset-name "${MSWE_DATASET}"
    -n "${NUM_EXAMPLES_MSWE}"
    -r "${ROLLOUTS}"
    -c "${MAX_CONCURRENT}"
    -w "${NUM_WORKERS}"
    --dataset-start-index "${DATASET_START_INDEX}"
    --max-turns "${MSWE_MAX_TURNS}"
    --max-judge-submissions "${MAX_JUDGE_SUBMISSIONS}"
    --run-root "${run_root}"
  )
  if [[ "${phase}" != "0" ]]; then
    if ((${#phase1_slice_flag[@]})); then
      args+=("${phase1_slice_flag[@]}")
    fi
  fi
  if [[ "${phase}" == "2" ]]; then
    args+=(--phase2-skill-max-chars "${PHASE2_SKILL_MAX_CHARS}")
  fi
  if ((${#allow_git_flag[@]})); then
    args+=("${allow_git_flag[@]}")
  fi
  if ((${#dry_flag[@]})); then
    args+=("${dry_flag[@]}")
  fi
  run_phase "${name}" "${args[@]}"
}

log "Serious run root: ${RUN_ROOT_BASE}"
log "Logs: ${LOG_DIR}"

run_lbp_phase 0
run_lbp_phase 1
run_lbp_phase 2

run_mswe_phase 0
run_mswe_phase 1
run_mswe_phase 2

if [[ "${DRY_RUN}" -eq 0 ]]; then
  run_phase "report-index" uv run ssl-experiment-report --root "${RUN_ROOT_BASE}"
fi

log ""
log "Done."
log "Run root: ${RUN_ROOT_BASE}"
log "Logs: ${LOG_DIR}"
