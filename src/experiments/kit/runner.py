"""Shared sequential factorial driver (one cell at a time, one summary row per cell)."""

from __future__ import annotations

import importlib
import logging
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any, TypeVar

from verifiers.utils.eval_utils import quiet_datasets

from experiments.kit.artifacts import write_run_summary
from experiments.kit.cells import parse_cell_filter
from experiments.kit.harness_contrast import phase1_harness_contrast_applicable, print_phase1_harness_contrast
from experiments.kit.registry import default_run_directory
from experiments.kit.reporting import CellRunSummary, print_comparison_table

logger = logging.getLogger(__name__)

T = TypeVar("T")


def import_env_modules(module_names: tuple[str, ...]) -> None:
    for name in module_names:
        importlib.import_module(name)


async def run_sequential_factorial(
    *,
    env_module_names: tuple[str, ...],
    cells: list[T],
    cells_filter: str | None,
    experiment_path_key: str,
    run_root: Path | None,
    spec_dict: dict[str, Any],
    evaluate_cell: Callable[[T, Path], Awaitable[CellRunSummary]],
    completion_banner: str,
) -> list[CellRunSummary]:
    """Load envs, filter cells, run one async eval per cell, write summary + table."""
    import_env_modules(env_module_names)
    selected = parse_cell_filter(cells_filter, cells)
    base = run_root or default_run_directory(experiment_path_key)
    base.mkdir(parents=True, exist_ok=True)

    rows: list[CellRunSummary] = []
    with quiet_datasets():
        for cell in selected:
            slug = cell.slug()  # type: ignore[attr-defined]
            cell_dir = base / slug
            cell_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Starting cell %s", slug)
            row = await evaluate_cell(cell, cell_dir)
            rows.append(row)
            logger.info("Finished cell %s avg_reward=%.4f", slug, row.avg_reward)

    _, report_path = write_run_summary(base, spec_dict, rows)
    print(f"\n{completion_banner}: {base.resolve()}")
    print(f"Markdown report: {report_path.resolve()}\n")
    print_comparison_table(rows)
    if phase1_harness_contrast_applicable(rows):
        print_phase1_harness_contrast(rows)
    return rows
