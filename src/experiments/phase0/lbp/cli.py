from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from verifiers import setup_logging
from verifiers.utils.eval_utils import get_log_level

from experiments.kit.cells import parse_cell_filter
from experiments.phase0.schema import Phase0Cell, Phase0Spec

from .eval_config import build_eval_config
from .runner import run_phase0_lbp


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=(
            "Phase 0: LongBench-Pro 2×2 — (total_score vs single_criterion) × (chat vs RLM). "
            "Envs are pulled in via repo `pyproject.toml` path deps (`uv sync`)."
        ),
    )
    p.add_argument("--model", "-m", default="openai/gpt-4.1-mini", help="Policy model id")
    p.add_argument("--judge-model", default="openai/gpt-4.1-mini", help="Judge model id")
    p.add_argument("--num-examples", "-n", type=int, default=5)
    p.add_argument("--rollouts-per-example", "-r", type=int, default=1)
    p.add_argument("--max-concurrent", "-c", type=int, default=2)
    p.add_argument(
        "--num-workers",
        "-w",
        default="auto",
        help='Env server workers (positive int or "auto")',
    )
    p.add_argument("--seed", type=int, default=42, help="Dataset shuffle seed when --shuffle is set")
    p.add_argument("--no-seed", action="store_true", help="Pass seed=None to envs")
    p.add_argument("--shuffle", action="store_true", help="Shuffle dataset with --seed")
    p.add_argument("--language", default="English")
    p.add_argument("--dataset-start-index", type=int, default=0)
    p.add_argument("--token-length", default="all")
    p.add_argument("--difficulty", default="all")
    p.add_argument("--max-turns-chat", type=int, default=8)
    p.add_argument("--max-turns-rlm", type=int, default=30)
    p.add_argument("--max-judge-submissions", type=int, default=8)
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
        help="Comma-separated slugs to run only (e.g. chat__total_score,rlm__single_criterion). Default: full 2×2.",
    )
    p.add_argument(
        "--run-root",
        type=Path,
        default=None,
        help="Directory for this run (default: outputs/experiments/phase0/lbp/<UTC timestamp>)",
    )
    p.add_argument("--dry-run", action="store_true", help="Print EvalConfig JSON per cell and exit")
    p.add_argument("--verbose", "-v", action="store_true")
    p.add_argument("--no-debug", action="store_true", help="Disable verifiers debug logging for eval")
    p.add_argument("--no-save-results", action="store_true")
    return p


def main() -> None:
    args = _build_parser().parse_args()
    if args.verbose:
        setup_logging(get_log_level(True))

    seed = None if args.no_seed else args.seed
    spec = Phase0Spec(
        model=args.model,
        judge_model=args.judge_model,
        num_examples=args.num_examples,
        rollouts_per_example=args.rollouts_per_example,
        max_concurrent=args.max_concurrent,
        num_workers=int(args.num_workers) if args.num_workers.isdigit() else args.num_workers,
        seed=seed,
        shuffle=args.shuffle,
        language=args.language,
        dataset_start_index=args.dataset_start_index,
        token_length=args.token_length,
        difficulty=args.difficulty,
        max_turns_chat=args.max_turns_chat,
        max_turns_rlm=args.max_turns_rlm,
        max_judge_submissions=args.max_judge_submissions,
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
                cell_output_dir=Path(".phase0_dry_run_lbp") / cell.slug(),
            )
            print(f"=== {cell.slug()} ===")
            print(cfg.model_dump_json(indent=2))
        return

    asyncio.run(
        run_phase0_lbp(
            spec,
            run_root=args.run_root,
            cells_filter=args.cells,
        )
    )


if __name__ == "__main__":
    main()
