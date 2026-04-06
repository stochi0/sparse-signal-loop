from __future__ import annotations

import logging
from dataclasses import asdict
from pathlib import Path
from typing import Any

from verifiers.utils.eval_utils import run_evaluation

from experiments.kit.reporting import CellRunSummary, summarize_cell
from experiments.kit.runner import run_sequential_factorial
from experiments.phase0.schema import Phase0Cell

from .env_args import env_id_for_cell
from .eval_config import build_eval_config
from .schema import MiniSwePhase0Spec

logger = logging.getLogger(__name__)


def _spec_for_json(spec: MiniSwePhase0Spec) -> dict[str, Any]:
    return asdict(spec)


async def run_mini_swe_phase0(
    spec: MiniSwePhase0Spec,
    *,
    run_root: Path | None = None,
    cells_filter: str | None = None,
) -> list[CellRunSummary]:
    async def evaluate_cell(cell: Phase0Cell, cell_dir: Path) -> CellRunSummary:
        cfg = build_eval_config(spec, cell, cell_output_dir=cell_dir)
        logger.info("env_id=%s", cfg.env_id)
        outputs = await run_evaluation(cfg)
        return summarize_cell(
            cell.slug(),
            cell.harness.value,
            cell.feedback.value,
            env_id_for_cell(cell),
            outputs,
        )

    return await run_sequential_factorial(
        env_module_names=("mini_swe_agent_plus", "mini_swe_agent_plus_rlm"),
        cells=Phase0Cell.factorial_design(),
        cells_filter=cells_filter,
        experiment_path_key="phase0/mini_swe",
        run_root=run_root,
        spec_dict=_spec_for_json(spec),
        evaluate_cell=evaluate_cell,
        completion_banner="Phase 0 (mini SWE) run directory",
    )
