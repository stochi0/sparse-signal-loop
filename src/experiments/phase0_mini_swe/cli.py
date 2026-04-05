from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from verifiers import setup_logging
from verifiers.utils.eval_utils import get_log_level

from experiments.phase0_lbp.runner import parse_cell_filter
from experiments.phase0_lbp.schema import Phase0Cell
from experiments.phase0_mini_swe.eval_config import build_eval_config
from experiments.phase0_mini_swe.runner import run_mini_swe_phase0
from experiments.phase0_mini_swe.schema import MiniSwePhase0Spec


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=(
            "Phase 0 (mini SWE): 2×2 — (total_score vs single_criterion) × "
            "(mini-swe-agent-plus vs mini-swe-agent-plus-rlm). "
            "Writes summary.json and REPORT.md under the run directory. "
            "Uses repo path deps after `uv sync`."
        ),
    )
    p.add_argument("--model", "-m", default="openai/gpt-4.1-mini", help="Policy model id")
    p.add_argument("--judge-model", default="openai/gpt-4.1-mini", help="Judge model id")
    p.add_argument("--num-examples", "-n", type=int, default=5)
    p.add_argument("--rollouts-per-example", "-r", type=int, default=1)
    p.add_argument("--max-concurrent", "-c", type=int, default=1)
    p.add_argument(
        "--num-workers",
        "-w",
        default="auto",
        help='Env server workers (positive int or "auto")',
    )
    p.add_argument(
        "--dataset-name",
        default="PrimeIntellect/SWE-Bench-Verified-Quick",
        choices=[
            "R2E-Gym/R2E-Gym-Subset",
            "SWE-bench/SWE-bench_Verified",
            "PrimeIntellect/SWE-Bench-Verified-Quick",
        ],
        help="HF dataset for SWE tasks",
    )
    p.add_argument("--dataset-start-index", type=int, default=0)
    p.add_argument(
        "--max-turns",
        type=int,
        default=80,
        help="Agent turns per rollout (use 80+ with in-loop judge; see env README)",
    )
    p.add_argument("--max-judge-submissions", type=int, default=8)
    p.add_argument(
        "--filter-repos",
        default=None,
        help="Comma-separated repo names to exclude from the dataset",
    )
    p.add_argument("--allow-git", action="store_true")
    p.add_argument(
        "--no-skip-swebench-install",
        action="store_true",
        help="Only affects the non-RLM env: run full swebench install (slower)",
    )
    p.add_argument("--env-dir-path", default="./environments")
    p.add_argument("--api-key-var", default="PRIME_API_KEY")
    p.add_argument("--api-base-url", default="https://api.pinference.ai/api/v1")
    p.add_argument(
        "--sampling-args",
        type=json.loads,
        default=None,
        help='Policy sampling JSON, e.g. \'{"temperature": 0.2, "max_tokens": 4096}\'',
    )
    p.add_argument(
        "--cells",
        default=None,
        help="Comma-separated slugs (e.g. chat__total_score,rlm__single_criterion). Default: full 2×2.",
    )
    p.add_argument(
        "--run-root",
        type=Path,
        default=None,
        help="Run directory (default: outputs/experiments/phase0_mini_swe/<UTC timestamp>)",
    )
    p.add_argument("--dry-run", action="store_true", help="Print EvalConfig JSON per cell and exit")
    p.add_argument("--verbose", "-v", action="store_true")
    p.add_argument("--no-debug", action="store_true")
    p.add_argument("--no-save-results", action="store_true")
    return p


def main() -> None:
    args = _build_parser().parse_args()
    if args.verbose:
        setup_logging(get_log_level(True))

    filter_repos = None
    if args.filter_repos:
        filter_repos = [s.strip() for s in args.filter_repos.split(",") if s.strip()]

    spec = MiniSwePhase0Spec(
        model=args.model,
        judge_model=args.judge_model,
        num_examples=args.num_examples,
        rollouts_per_example=args.rollouts_per_example,
        max_concurrent=args.max_concurrent,
        num_workers=int(args.num_workers) if args.num_workers.isdigit() else args.num_workers,
        dataset_name=args.dataset_name,
        dataset_start_index=args.dataset_start_index,
        max_turns=args.max_turns,
        max_judge_submissions=args.max_judge_submissions,
        filter_repos=filter_repos,
        allow_git=args.allow_git,
        skip_swebench_install=not args.no_skip_swebench_install,
        env_dir_path=args.env_dir_path,
        api_key_var=args.api_key_var,
        api_base_url=args.api_base_url,
        sampling_args=args.sampling_args or {},
        verbose=args.verbose,
        debug=not args.no_debug,
        save_results=not args.no_save_results,
    )

    if args.dry_run:
        cells = parse_cell_filter(args.cells, Phase0Cell.factorial_design())
        for cell in cells:
            cfg = build_eval_config(
                spec,
                cell,
                cell_output_dir=Path(".phase0_dry_run_msap") / cell.slug(),
            )
            print(f"=== {cell.slug()} ===")
            print(cfg.model_dump_json(indent=2))
        return

    asyncio.run(
        run_mini_swe_phase0(
            spec,
            run_root=args.run_root,
            cells_filter=args.cells,
        )
    )


if __name__ == "__main__":
    main()
