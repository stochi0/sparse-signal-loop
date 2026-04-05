from __future__ import annotations

import importlib
import logging
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from verifiers.utils.eval_utils import quiet_datasets, run_evaluation

from experiments.run_artifacts import write_run_summary

from .env_args import env_id_for_cell
from .eval_config import build_eval_config
from .reporting import (
    Phase0CellSummary,
    print_comparison_table,
    summarize_cell,
)
from .schema import Phase0Cell, Phase0Spec

logger = logging.getLogger(__name__)


def ensure_env_modules_loaded() -> None:
    for mod in ("longbenchpro", "longbenchpro_rlm"):
        importlib.import_module(mod)


def _spec_for_json(spec: Phase0Spec) -> dict[str, Any]:
    return asdict(spec)


def parse_cell_filter(slugs: str | None, cells: list[Phase0Cell]) -> list[Phase0Cell]:
    if not slugs:
        return list(cells)
    order = [s.strip() for s in slugs.split(",") if s.strip()]
    by_slug = {c.slug(): c for c in cells}
    missing = set(order) - set(by_slug.keys())
    if missing:
        raise ValueError(f"Unknown cell slug(s): {sorted(missing)}. Valid: {sorted(by_slug)}")
    return [by_slug[s] for s in order]


async def run_phase0_lbp(
    spec: Phase0Spec,
    *,
    run_root: Path | None = None,
    cells_filter: str | None = None,
) -> list[Phase0CellSummary]:
    """Run each selected factorial cell sequentially; return per-cell summaries."""
    ensure_env_modules_loaded()
    all_cells = Phase0Cell.factorial_design()
    selected = parse_cell_filter(cells_filter, all_cells)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    base = run_root or Path("outputs/experiments/phase0_lbp") / stamp
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
                )
            )
            logger.info("Finished cell %s avg_reward=%.4f", slug, rows[-1].avg_reward)

    _, report_path = write_run_summary(base, _spec_for_json(spec), rows)
    print(f"\nPhase 0 run directory: {base.resolve()}")
    print(f"Markdown report: {report_path.resolve()}\n")
    print_comparison_table(rows)
    return rows
