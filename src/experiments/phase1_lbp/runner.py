from __future__ import annotations

import importlib
import logging
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from verifiers.utils.eval_utils import quiet_datasets, run_evaluation

from experiments.cell_utils import parse_cell_filter
from experiments.phase0_lbp.reporting import (
    Phase0CellSummary,
    print_comparison_table,
    summarize_cell,
)
from experiments.phase1_common.schema import Phase1Cell
from experiments.run_artifacts import write_run_summary

from .env_args import env_id_for_cell
from .eval_config import build_eval_config
from .schema import Phase1LbpSpec

logger = logging.getLogger(__name__)


def ensure_env_modules_loaded() -> None:
    for mod in ("longbenchpro", "longbenchpro_rlm"):
        importlib.import_module(mod)


def _spec_for_json(spec: Phase1LbpSpec) -> dict[str, Any]:
    return asdict(spec)


async def run_phase1_lbp(
    spec: Phase1LbpSpec,
    *,
    run_root: Path | None = None,
    cells_filter: str | None = None,
) -> list[Phase0CellSummary]:
    """Run each selected Phase 1 cell sequentially; return per-cell summaries."""
    ensure_env_modules_loaded()
    all_cells = Phase1Cell.factorial_design()
    selected = parse_cell_filter(cells_filter, all_cells)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    base = run_root or Path("outputs/experiments/phase1_lbp") / stamp
    base.mkdir(parents=True, exist_ok=True)

    rows: list[Phase0CellSummary] = []
    with quiet_datasets():
        for cell in selected:
            slug = cell.slug()
            cell_dir = base / slug
            cell_dir.mkdir(parents=True, exist_ok=True)
            cfg = build_eval_config(spec, cell, cell_output_dir=cell_dir)
            logger.info("Starting cell %s (%s)", slug, cfg.env_id)
            outputs = await run_evaluation(cfg)
            rows.append(
                summarize_cell(
                    slug,
                    cell.harness.value,
                    cell.feedback.value,
                    env_id_for_cell(cell),
                    outputs,
                    memory=cell.memory.value,
                )
            )
            logger.info("Finished cell %s avg_reward=%.4f", slug, rows[-1].avg_reward)

    _, report_path = write_run_summary(base, _spec_for_json(spec), rows)
    print(f"\nPhase 1 (LBP) run directory: {base.resolve()}")
    print(f"Markdown report: {report_path.resolve()}\n")
    print_comparison_table(rows)
    return rows
