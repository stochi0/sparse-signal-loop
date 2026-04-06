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
from .runner import run_phase2_lbp
from .schema import Phase2LbpSpec


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=(
            "Phase 2 (LongBench-Pro): self-improving harness — RLM maintains ``SKILL.md`` in the sandbox; "
            "chat baselines use the same in-loop judge feedback without a file, or ``<phase2_skill>`` reinject. "
            "Six cells: (rlm_skill_file | chat_no_file | chat_system_reinject) × (total_score | single_criterion). "
            "Uses ``phase2_skill_mode``, ``phase2_skill_max_chars``, ``phase1_slice``; ``phase1_working_memory`` is off."
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
    p.add_argument("--token-length", default="all", help="Passed to env; slice still pins 32k when phase1_slice")
    p.add_argument("--difficulty", default="all")
    p.add_argument("--max-turns-chat", type=int, default=8)
    p.add_argument("--max-turns-rlm", type=int, default=30)
    p.add_argument("--max-judge-submissions", type=int, default=8)
    p.add_argument(
        "--phase2-skill-max-chars",
        type=int,
        default=6000,
        help="Soft cap (prompt + seed SKILL.md); reinjected chat skill is truncated to this length",
    )
    p.add_argument(
        "--no-phase1-slice",
        action="store_true",
        help="Disable env phase1_slice (no T6.1 @ 32k default pinning)",
    )
    p.add_argument(
        "--smoke",
        action="store_true",
        help=(
            "Fast 1×1 smoke preset: num_examples=1, rollouts=1, max_concurrent=1, num_workers=1, "
            "fewer chat/RLM turns and judge submissions, smaller phase2 skill cap, "
            "higher RLM sandbox CPU/RAM and shorter sub-REPL depth. "
            "Default cells: one chat cell (no Docker); pass --cells … for RLM smoke."
        ),
    )
    p.add_argument(
        "--rlm-sandbox-cpu",
        type=int,
        default=None,
        help="RLM only: sandbox_cpu_cores (longbenchpro-rlm)",
    )
    p.add_argument(
        "--rlm-sandbox-memory-gb",
        type=int,
        default=None,
        help="RLM only: sandbox_memory_gb",
    )
    p.add_argument(
        "--rlm-sandbox-disk-gb",
        type=int,
        default=None,
        help="RLM only: sandbox_disk_size_gb",
    )
    p.add_argument(
        "--rlm-sandbox-timeout-minutes",
        type=int,
        default=None,
        help="RLM only: sandbox_timeout_minutes",
    )
    p.add_argument(
        "--rlm-code-exec-timeout",
        type=int,
        default=None,
        help="RLM only: code_execution_timeout (seconds per REPL run)",
    )
    p.add_argument(
        "--rlm-sub-llm-max-turns",
        type=int,
        default=None,
        help="RLM only: sub_llm_max_turns (tool turns inside each REPL call)",
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
        help="Directory for this run (default: outputs/experiments/phase2/lbp/<UTC timestamp>)",
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

    if args.smoke:
        args.num_examples = 1
        args.rollouts_per_example = 1
        args.max_concurrent = 1
        args.num_workers = "1"
        args.max_turns_chat = 4
        args.max_turns_rlm = 10
        args.max_judge_submissions = 2
        args.phase2_skill_max_chars = min(args.phase2_skill_max_chars, 2500)
        if not args.cells:
            args.cells = "chat__total_score__chat_no_file"
        # RLM cells still get a beefier sandbox when you override --cells (optional CLI can replace)
        if args.rlm_sandbox_cpu is None:
            args.rlm_sandbox_cpu = 4
        if args.rlm_sandbox_memory_gb is None:
            args.rlm_sandbox_memory_gb = 8
        if args.rlm_sandbox_disk_gb is None:
            args.rlm_sandbox_disk_gb = 8
        if args.rlm_sandbox_timeout_minutes is None:
            args.rlm_sandbox_timeout_minutes = 45
        if args.rlm_code_exec_timeout is None:
            args.rlm_code_exec_timeout = 60
        if args.rlm_sub_llm_max_turns is None:
            args.rlm_sub_llm_max_turns = 3

    seed = None if args.no_seed else args.seed
    spec = Phase2LbpSpec(
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
        phase1_slice=not args.no_phase1_slice,
        phase2_skill_max_chars=args.phase2_skill_max_chars,
        rlm_sandbox_cpu_cores=args.rlm_sandbox_cpu,
        rlm_sandbox_memory_gb=args.rlm_sandbox_memory_gb,
        rlm_sandbox_disk_size_gb=args.rlm_sandbox_disk_gb,
        rlm_sandbox_timeout_minutes=args.rlm_sandbox_timeout_minutes,
        rlm_code_execution_timeout=args.rlm_code_exec_timeout,
        rlm_sub_llm_max_turns=args.rlm_sub_llm_max_turns,
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
                cell_output_dir=Path(".phase2_dry_run_lbp") / cell.slug(),
            )
            print(f"=== {cell.slug()} ===")
            print(cfg.model_dump_json(indent=2))
        return

    asyncio.run(
        run_phase2_lbp(
            spec,
            run_root=args.run_root,
            cells_filter=args.cells,
        )
    )


if __name__ == "__main__":
    main()
