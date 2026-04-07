from __future__ import annotations

import logging
from dataclasses import asdict
from pathlib import Path
from typing import Any

from verifiers.utils.eval_utils import run_evaluation

from experiments.kit.reporting import CellRunSummary, summarize_cell
from experiments.kit.runner import run_sequential_factorial
from experiments.phase2.schema import Phase2Cell

from .env_args import env_id_for_cell
from .eval_config import build_eval_config
from .schema import Phase2MiniSweSpec

logger = logging.getLogger(__name__)


def _spec_for_json(spec: Phase2MiniSweSpec) -> dict[str, Any]:
    return asdict(spec)


async def run_phase2_mini_swe(
    spec: Phase2MiniSweSpec,
    *,
    run_root: Path | None = None,
    cells_filter: str | None = None,
) -> list[CellRunSummary]:
    async def evaluate_cell(cell: Phase2Cell, cell_dir: Path) -> CellRunSummary:
        cfg = build_eval_config(spec, cell, cell_output_dir=cell_dir)
        logger.info("env_id=%s", cfg.env_id)
        outputs = await run_evaluation(cfg)
        return summarize_cell(
            cell.slug(),
            cell.harness.value,
            cell.feedback.value,
            env_id_for_cell(cell),
            outputs,
            skill_arm=cell.arm.value,
        )

    return await run_sequential_factorial(
        env_module_names=("mini_swe_agent_plus", "mini_swe_agent_plus_rlm"),
        cells=Phase2Cell.factorial_design(),
        cells_filter=cells_filter,
        experiment_path_key="phase2/mini_swe",
        run_root=run_root,
        spec_dict=_spec_for_json(spec),
        evaluate_cell=evaluate_cell,
        completion_banner="Phase 2 (mini SWE) run directory",
    )

