"""Experiment output layout and human-readable report titles.

Each CLI registers a path key (posix, relative to ``outputs/experiments``), e.g. ``phase0/lbp``.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

EXPERIMENTS_OUTPUT_ROOT = Path("outputs/experiments")

# Key: path under EXPERIMENTS_OUTPUT_ROOT (no leading/trailing slashes).
BENCHMARK_LABELS: dict[str, str] = {
    "phase0/lbp": "LongBench-Pro (LBP)",
    "phase0/mini_swe": "Mini SWE Agent Plus (MSAP)",
    "phase1/lbp": "LongBench-Pro · Phase 1 (working memory)",
    "phase1/mini_swe": "Mini SWE Agent Plus · Phase 1 (working memory)",
    "phase2/lbp": "LongBench-Pro · Phase 2 (SKILL.md vs chat baselines)",
}


def benchmark_label(experiment_path_key: str) -> str:
    return BENCHMARK_LABELS.get(experiment_path_key, experiment_path_key)


def experiment_relative_id(run_dir: Path) -> str:
    """Directory under ``outputs/experiments`` that contains this run (e.g. ``phase0/lbp``)."""
    run_dir = run_dir.resolve()
    root = EXPERIMENTS_OUTPUT_ROOT.resolve()
    parent = run_dir.parent
    try:
        return parent.relative_to(root).as_posix()
    except ValueError:
        return parent.name


def default_run_directory(experiment_path_key: str, *, stamp: str | None = None) -> Path:
    """``outputs/experiments/<key>/<UTC stamp>`` (directories are not created here)."""
    ts = stamp or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return EXPERIMENTS_OUTPUT_ROOT / experiment_path_key / ts
