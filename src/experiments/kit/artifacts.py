"""Persist ``summary.json`` + ``REPORT.md`` for factorial runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from experiments.kit.reporting import CellRunSummary
from experiments.kit.run_report_md import write_run_report_md_from_payload


def write_run_summary(run_dir: Path, spec_dict: dict[str, Any], rows: list[CellRunSummary]) -> tuple[Path, Path]:
    """Write ``summary.json`` and ``REPORT.md`` under ``run_dir``; return both paths."""
    run_dir.mkdir(parents=True, exist_ok=True)
    summary_path = run_dir / "summary.json"
    payload = {"spec": spec_dict, "cells": [r.to_json_dict() for r in rows]}
    summary_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    report_path = write_run_report_md_from_payload(run_dir, payload)
    return summary_path, report_path
