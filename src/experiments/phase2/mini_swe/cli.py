from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from verifiers import setup_logging
from verifiers.utils.eval_utils import get_log_level

from experiments.kit.cells import parse_cell_filter
from experiments.phase2.schema import Phase2Cell

from .eval_config import build_eval_config
from .runner import run_phase2_mini_swe
from .schema import Phase2MiniSweSpec


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=(
            "Phase 2 (mini SWE): self-improving skill harness arms (Phase2Cell) on mini-swe-agent-plus envs. "
            "Six cells: (rlm_skill_file | chat_no_file | chat_system_reinject) × "
            "(total_score | single_criterion). "
            "Uses ``phase2_skill_mode``, ``phase2_skill_max_chars`` and ``phase1_slice``; "
            "``phase1_working_memory`` is forced off."
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
        help="Agent turns per rollout (use 80+ with in-loop judge)",
    )
    p.add_argument("--max-judge-submissions", type=int, default=8)
    p.add_argument(
        "--filter-repos",
        default=None,
        help="Comma-separated repo names to exclude from the dataset",
    )
    p.add_argument(
        "--only-repos",
        default=None,
        help="Comma-separated repo allow-list (overrides default phase1_slice sweepbench filtering when enabled)",
    )
    p.add_argument("--allow-git", action="store_true")
    p.add_argument(
        "--no-skip-swebench-install",
        action="store_true",
        help="Only affects the non-RLM env: run full swebench install (slower)",
    )
    p.add_argument(
        "--phase2-skill-max-chars",
        type=int,
        default=6000,
        help="Soft cap (prompted; reinject baseline truncates to this length)",
    )
    p.add_argument(
        "--no-phase1-slice",
        action="store_true",
        help="Disable env phase1_slice (no default django-only filtering on swebench datasets)",
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
        help=(
            "Comma-separated slugs (default: all 6). Example: "
            "rlm__total_score__rlm_skill_file,chat__single_criterion__chat_system_reinject"
        ),
    )
    p.add_argument(
        "--run-root",
        type=Path,
        default=None,
        help="Run directory (default: outputs/experiments/phase2/mini_swe/<UTC timestamp>)",
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

    only_repos = None
    if args.only_repos:
        only_repos = [s.strip() for s in args.only_repos.split(",") if s.strip()]

    spec = Phase2MiniSweSpec(
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
        only_repos=only_repos,
        allow_git=args.allow_git,
        skip_swebench_install=not args.no_skip_swebench_install,
        phase1_slice=not args.no_phase1_slice,
        phase2_skill_max_chars=args.phase2_skill_max_chars,
        env_dir_path=args.env_dir_path,
        api_key_var=args.api_key_var,
        api_base_url=args.api_base_url,
        sampling_args=args.sampling_args or {},
        verbose=args.verbose,
        debug=not args.no_debug,
        save_results=not args.no_save_results,
    )

    if args.dry_run:
        cells = parse_cell_filter(args.cells, Phase2Cell.factorial_design())
        for cell in cells:
            cfg = build_eval_config(
                spec,
                cell,
                cell_output_dir=Path(".phase2_dry_run_msap") / cell.slug(),
            )
            print(f"=== {cell.slug()} ===")
            print(cfg.model_dump_json(indent=2))
        return

    asyncio.run(
        run_phase2_mini_swe(
            spec,
            run_root=args.run_root,
            cells_filter=args.cells,
        )
    )


if __name__ == "__main__":
    main()

