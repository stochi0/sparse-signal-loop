## Sparse Signal Loop

Sparse Signal Loop is a research harness for evaluating LLM agents across progressive interventions on two benchmark families:

- LongBench-Pro (LBP)
- Mini SWE Agent Plus (MSAP)

It compares chat-style and RLM-style harnesses across three phases:

- Phase 0: baseline harness/feedback comparisons
- Phase 1: working-memory interventions
- Phase 2: self-improving skill mechanisms (`SKILL.md` and chat reinjection baselines)

## Repository Layout

- `src/experiments`: phase schemas, CLIs, factorial runner, summary/report generation.
- `src/envs/longbenchpro`: LBP chat harness environment package.
- `src/envs/longbenchpro_rlm`: LBP RLM harness environment package.
- `src/envs/mini_swe_agent_plus`: mini-SWE chat harness environment package.
- `src/envs/mini_swe_agent_plus_rlm`: mini-SWE RLM harness environment package.
- `scripts`: practical wrappers for smoke runs, phase runs, full matrix runs, and Prime pod helpers.
- `archive`: archived outputs.

## Prerequisites

- Python `3.11+`
- `uv` (the scripts can install it if missing)
- Prime API access for real runs (`PRIME_API_KEY`)

## Quickstart (Local)

1) Install dependencies

```bash
uv sync
```

2) Add environment variables

```bash
printf "PRIME_API_KEY=%s\n" "<your_prime_api_key>" > .env
```

3) Run a dry-run smoke

```bash
./scripts/smoke.sh --dry-run
```

4) Run a real smoke

```bash
./scripts/smoke.sh
```

Smoke logs are written to `outputs/smoke_logs/<timestamp>/`.

## Running Experiments

### Per-phase scripts

LBP:

```bash
./scripts/phase0/lbp.sh -n 4 -r 1
./scripts/phase1/lbp.sh --smoke
./scripts/phase2/lbp.sh --smoke
```

Mini-SWE:

```bash
./scripts/phase0/mini_swe.sh -n 4 -r 1
./scripts/phase1/mini_swe.sh --smoke
./scripts/phase2/mini_swe.sh --smoke
```

### Full matrix run

Runs phase0/1/2 for both LBP and mini-SWE:

```bash
./scripts/big_run.sh
```

Use `--dry-run` on any script to validate configuration without API calls.

## CLI Entry Points

The package exposes these commands via `uv run`:

- `ssl-phase0-lbp`
- `ssl-phase0-msap`
- `ssl-phase1-lbp`
- `ssl-phase1-msap`
- `ssl-phase2-lbp`
- `ssl-phase2-msap`
- `ssl-experiment-report`

Example:

```bash
uv run ssl-phase0-lbp --dry-run
```

## Environment Variables

Common:

- `PRIME_API_KEY`: required unless `--dry-run`.
- `ENV_FILE`: optional explicit dotenv path.
- `REPO_DIR`: optional repo path used by shared dotenv loader.

Common run knobs (also script flags):

- `POLICY_MODEL`
- `JUDGE_MODEL`
- `DATASET_START_INDEX`
- `NUM_EXAMPLES`
- `ROLLOUTS`

Mini-SWE:

- `MSWE_DATASET` (defaults to `PrimeIntellect/SWE-Bench-Verified-Quick`)
- `ALLOW_GIT` (for tool-level git operations in mini-SWE envs)

Prime pod helpers:

- `SPARSE_SIGNAL_LOOP_REPO`
- `PRIME_POD_SKU`
- `PRIME_API_BASE_URL`
- `SSH_KEY_NAME`

LBP RLM:

- `LBP_RLM_CONTEXT_CACHE` (optional context cache path override)

## Outputs and Reporting

Run outputs are written under `outputs/` (for example `outputs/experiments/...` and `outputs/serious_runs/...`).

Each run directory includes structured artifacts such as:

- `summary.json`
- `REPORT.md`

Regenerate reports for a root directory:

```bash
uv run ssl-experiment-report --root outputs/experiments
```

Regenerate for a single run directory:

```bash
uv run ssl-experiment-report --run-dir outputs/experiments/<phase>/<dataset>/<timestamp>
```

## Prime Pod Workflow

### 1) On your laptop

Upload SSH key (one-time):

```bash
./scripts/prime_ssh_key_upload.sh ~/.ssh/id_ed25519.pub
prime config set-ssh-key-path ~/.ssh/id_ed25519
```

Create pod and connect:

```bash
# optional: export PRIME_POD_SKU=6ac679
./scripts/prime_pod.sh create
prime pods list
prime pods ssh <pod-id>
```

### 2) On the pod

Bootstrap repo and dependencies:

```bash
export SPARSE_SIGNAL_LOOP_REPO="https://github.com/<YOU>/sparse-signal-loop.git"
./scripts/prime_pod.sh bootstrap
cd ~/sparse-signal-loop
```

Run a smoke:

```bash
./scripts/smoke.sh
```

### 3) Cleanup

```bash
prime pods terminate <pod-id>
```

## Environment Package Docs

- `src/envs/longbenchpro/README.md`
- `src/envs/longbenchpro_rlm/README.md`
- `src/envs/mini_swe_agent_plus/README.md`
- `src/envs/mini_swe_agent_plus_rlm/README.md`

## Linting

Run lint checks:

```bash
uv run ruff check .
uv run ruff format --check .
```

