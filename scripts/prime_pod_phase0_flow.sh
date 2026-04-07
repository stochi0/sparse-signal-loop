#!/usr/bin/env bash
# Prime Pod flow: create a cheap CPU pod, bootstrap it, run Phase 0 evals in tmux.
#
# Local (your Mac / laptop):
#   PRIME_POD_SKU=6ac679 ./scripts/prime_pod_phase0_flow.sh create
#   ./scripts/prime_pod_phase0_flow.sh help-status
#   prime pods ssh <pod-id>
#
# SSH: if "Permission denied (publickey)", register your pubkey with Prime, then use a new pod:
#   ./scripts/prime_upload_ssh_pubkey.sh
#   prime config set-ssh-key-path ~/.ssh/id_ed25519   # private key matching that .pub
#
# On the pod (after SSH), copy this repo or set SPARSE_SIGNAL_LOOP_REPO and run:
#   curl -fsSL -o /tmp/flow.sh <raw-url-to-this-script>   # optional
#   SPARSE_SIGNAL_LOOP_REPO=https://github.com/YOU/sparse-signal-loop.git \
#     ./scripts/prime_pod_phase0_flow.sh bootstrap
#   ./scripts/prime_pod_phase0_flow.sh run-lbp   # PRIME_API_KEY etc. from .env
#
# Phase 1 only, smallest run (1 example, 1 rollout):
#   ./scripts/prime_pod_phase0_flow.sh run-phase1-lbp-smoke
#   # or: NUM_EXAMPLES=1 ROLLOUTS=1 ./scripts/prime_pod_phase0_flow.sh run-phase1-lbp
#
# Or from a machine that already has the repo cloned at REPO_DIR:
#   ./scripts/prime_pod_phase0_flow.sh bootstrap   # skips clone if REPO_DIR exists and is a git repo
#
# Dotenv: sources the first file that exists — \$ENV_FILE, then \$REPO_DIR/.env, then repo-root
# .env next to this script (e.g. sparse-signal-loop/.env). Override with ENV_FILE=/path/to/.env
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

PRIME_POD_SKU="${PRIME_POD_SKU:-6ac679}"
REPO_DIR="${REPO_DIR:-${HOME}/sparse-signal-loop}"
SPARSE_SIGNAL_LOOP_REPO="${SPARSE_SIGNAL_LOOP_REPO:-}"

POLICY_MODEL="${POLICY_MODEL:-z-ai/glm-4.7}"
JUDGE_MODEL="${JUDGE_MODEL:-z-ai/glm-4.7-flash}"
NUM_EXAMPLES="${NUM_EXAMPLES:-4}"
DATASET_START_INDEX="${DATASET_START_INDEX:-0}"
ROLLOUTS="${ROLLOUTS:-1}"

TMUX_SESSION="${TMUX_SESSION:-phase0-eval}"

die() {
  echo "error: $*" >&2
  exit 1
}

# Load KEY=value pairs into the environment (export). Tries ENV_FILE, then REPO_DIR/.env, then REPO_ROOT/.env.
load_dotenv() {
  local f=""
  if [[ -n "${ENV_FILE:-}" ]]; then
    [[ -f "${ENV_FILE}" ]] || die "ENV_FILE set but not found: ${ENV_FILE}"
    f="${ENV_FILE}"
  elif [[ -f "${REPO_DIR}/.env" ]]; then
    f="${REPO_DIR}/.env"
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

ensure_uv() {
  if command -v uv >/dev/null 2>&1; then
    return 0
  fi
  echo "Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # shellcheck disable=SC1091
  [[ -f "${HOME}/.local/bin/env" ]] && source "${HOME}/.local/bin/env"
  export PATH="${HOME}/.local/bin:${PATH}"
  command -v uv >/dev/null 2>&1 || die "uv not found after install; add ~/.local/bin to PATH"
}

cmd_create() {
  echo "Creating pod with availability id ${PRIME_POD_SKU} (CPU non-spot ~\$0.03/hr if still priced there)."
  prime pods create --id "${PRIME_POD_SKU}"
}

cmd_help_status() {
  cat <<'EOF'
Next steps (run on your local machine):

  prime pods list
  prime pods status <pod-id>
  prime pods ssh <pod-id>

If ssh says "Permission denied (publickey)": Prime only installs SSH keys that are on your account.
From the repo (uses PRIME_API_KEY from .env):

  ./scripts/prime_upload_ssh_pubkey.sh
  prime config set-ssh-key-path ~/.ssh/id_ed25519

Then create a new pod and ssh again — VMs provisioned before the key was uploaded may not get it.

When finished (stops billing):

  prime pods terminate <pod-id>
EOF
}

cmd_bootstrap() {
  sudo apt-get update
  sudo apt-get install -y git curl build-essential

  ensure_uv

  if [[ -d "${REPO_DIR}/.git" ]]; then
    echo "Repo already present at ${REPO_DIR}; pulling..."
    git -C "${REPO_DIR}" pull --ff-only || true
  else
    [[ -n "${SPARSE_SIGNAL_LOOP_REPO}" ]] || die "Set SPARSE_SIGNAL_LOOP_REPO to your git clone URL, or clone into REPO_DIR first"
    git clone "${SPARSE_SIGNAL_LOOP_REPO}" "${REPO_DIR}"
  fi

  (cd "${REPO_DIR}" && uv sync)
  echo "Bootstrap done. Ensure .env is in ${REPO_DIR} (or set ENV_FILE), then: $0 run-lbp | run-msap | run-both | run-phase1-lbp | run-phase1-msap | run-phase1-lbp-smoke"
}

_run_in_tmux() {
  local name="$1"
  shift
  local cmd="$*"

  if ! command -v tmux >/dev/null 2>&1; then
    sudo apt-get install -y tmux
  fi

  tmux has-session -t "${name}" 2>/dev/null && tmux kill-session -t "${name}"
  # shellcheck disable=SC2087
  tmux new-session -d -s "${name}" bash -c "cd '${REPO_DIR}' && ${cmd}; echo; echo '(exit code' \$?') — session stays open'; exec bash"

  echo "Started tmux session '${name}'. Attach with: tmux attach -t ${name}"
}

cmd_run_lbp() {
  [[ -d "${REPO_DIR}" ]] || die "REPO_DIR missing: ${REPO_DIR} (run bootstrap first)"
  [[ -n "${PRIME_API_KEY:-}" ]] || echo "warning: PRIME_API_KEY is unset"

  _run_in_tmux "${TMUX_SESSION}-lbp" \
    "uv run ssl-phase0-lbp -m '${POLICY_MODEL}' --judge-model '${JUDGE_MODEL}' -n ${NUM_EXAMPLES} --dataset-start-index ${DATASET_START_INDEX} -r ${ROLLOUTS}"
}

cmd_run_msap() {
  [[ -d "${REPO_DIR}" ]] || die "REPO_DIR missing: ${REPO_DIR} (run bootstrap first)"
  [[ -n "${PRIME_API_KEY:-}" ]] || echo "warning: PRIME_API_KEY is unset"

  _run_in_tmux "${TMUX_SESSION}-msap" \
    "uv run ssl-phase0-msap -m '${POLICY_MODEL}' --judge-model '${JUDGE_MODEL}' -n ${NUM_EXAMPLES} --dataset-start-index ${DATASET_START_INDEX} -r ${ROLLOUTS}"
}

cmd_run_both() {
  cmd_run_lbp
  cmd_run_msap
  echo "Both started in separate tmux sessions: ${TMUX_SESSION}-lbp and ${TMUX_SESSION}-msap"
}

cmd_run_phase1_lbp() {
  [[ -d "${REPO_DIR}" ]] || die "REPO_DIR missing: ${REPO_DIR} (run bootstrap first)"
  [[ -n "${PRIME_API_KEY:-}" ]] || echo "warning: PRIME_API_KEY is unset"

  _run_in_tmux "${TMUX_SESSION}-p1-lbp" \
    "uv run ssl-phase1-lbp -m '${POLICY_MODEL}' --judge-model '${JUDGE_MODEL}' -n ${NUM_EXAMPLES} --dataset-start-index ${DATASET_START_INDEX} -r ${ROLLOUTS}"
}

# Phase 1 LBP with fixed -n 1 -r 1 (ignores NUM_EXAMPLES / ROLLOUTS). Use run-phase1-lbp + env vars for custom sizes.
cmd_run_phase1_lbp_smoke() {
  [[ -d "${REPO_DIR}" ]] || die "REPO_DIR missing: ${REPO_DIR} (run bootstrap first)"
  [[ -n "${PRIME_API_KEY:-}" ]] || echo "warning: PRIME_API_KEY is unset"

  _run_in_tmux "${TMUX_SESSION}-p1-lbp-smoke" \
    "uv run ssl-phase1-lbp -m '${POLICY_MODEL}' --judge-model '${JUDGE_MODEL}' -n 1 --dataset-start-index ${DATASET_START_INDEX} -r 1"
}

cmd_run_phase1_msap() {
  [[ -d "${REPO_DIR}" ]] || die "REPO_DIR missing: ${REPO_DIR} (run bootstrap first)"
  [[ -n "${PRIME_API_KEY:-}" ]] || echo "warning: PRIME_API_KEY is unset"

  _run_in_tmux "${TMUX_SESSION}-p1-msap" \
    "uv run ssl-phase1-msap -m '${POLICY_MODEL}' --judge-model '${JUDGE_MODEL}' -n ${NUM_EXAMPLES} --dataset-start-index ${DATASET_START_INDEX} -r ${ROLLOUTS}"
}

cmd_help() {
  cat <<EOF
Usage: $0 <command>

  create       Local: prime pods create --id \${PRIME_POD_SKU:-6ac679}
  help-status  Print follow-up prime pods commands
  bootstrap    On pod: apt deps, install uv, clone repo (needs SPARSE_SIGNAL_LOOP_REPO) or update REPO_DIR, uv sync
  run-lbp      On pod: tmux session ${TMUX_SESSION}-lbp → ssl-phase0-lbp
  run-msap     On pod: tmux session ${TMUX_SESSION}-msap → ssl-phase0-msap
  run-both     On pod: start both tmux sessions
  run-phase1-lbp   On pod: ${TMUX_SESSION}-p1-lbp → ssl-phase1-lbp (6-cell grid + RLM vs chat summary)
  run-phase1-lbp-smoke  Same as run-phase1-lbp but fixed -n 1 -r 1 (smallest useful smoke test)
  run-phase1-msap  On pod: ${TMUX_SESSION}-p1-msap → ssl-phase1-msap

Environment (optional overrides):

  PRIME_POD_SKU          Availability id (default: 6ac679)
  REPO_DIR               Clone path (default: ~/sparse-signal-loop)
  SPARSE_SIGNAL_LOOP_REPO Git URL for bootstrap clone
  POLICY_MODEL           (default: ${POLICY_MODEL})
  JUDGE_MODEL            (default: ${JUDGE_MODEL})
  NUM_EXAMPLES           (default: ${NUM_EXAMPLES}; not used by run-phase1-lbp-smoke)
  DATASET_START_INDEX    (default: ${DATASET_START_INDEX})
  ROLLOUTS               (default: ${ROLLOUTS}; not used by run-phase1-lbp-smoke)
  PRIME_API_KEY          Required for eval API calls (often set via .env)
  TMUX_SESSION           Prefix for session names (default: phase0-eval)
  ENV_FILE               Explicit path to dotenv (default: try REPO_DIR/.env then repo-root .env)
EOF
}

main() {
  local sub="${1:-help}"
  if [[ "${sub}" != help && "${sub}" != -h && "${sub}" != --help && "${sub}" != help-status ]]; then
    load_dotenv
  fi
  case "${sub}" in
    create) cmd_create ;;
    help-status) cmd_help_status ;;
    bootstrap) cmd_bootstrap ;;
    run-lbp) cmd_run_lbp ;;
    run-msap) cmd_run_msap ;;
    run-both) cmd_run_both ;;
    run-phase1-lbp) cmd_run_phase1_lbp ;;
    run-phase1-lbp-smoke) cmd_run_phase1_lbp_smoke ;;
    run-phase1-msap) cmd_run_phase1_msap ;;
    help | -h | --help) cmd_help ;;
    *) die "unknown command: ${sub}; try: $0 help" ;;
  esac
}

main "$@"
