"""Concise Markdown reports for phase-0 experiment runs (from ``summary.json``)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Run folder name (under outputs/experiments/<name>/…) → human benchmark label.
_EXPERIMENT_BENCHMARK: dict[str, str] = {
    "phase0_lbp": "LongBench-Pro (LBP)",
    "phase0_mini_swe": "Mini SWE Agent Plus (MSAP)",
}


def _benchmark_label(experiment_dir_name: str) -> str:
    return _EXPERIMENT_BENCHMARK.get(experiment_dir_name, experiment_dir_name)


def _fmt_num(x: float | None, *, digits: int = 4, na: str = "—") -> str:
    if x is None:
        return na
    return f"{x:.{digits}f}"


def _fmt_int(x: float | None, na: str = "—") -> str:
    if x is None:
        return na
    return f"{int(round(x)):,}"


def _key_metric(metrics: dict[str, Any]) -> str:
    for k in ("task_metric_reward", "solved", "judge_reward"):
        if k in metrics:
            v = metrics[k]
            if isinstance(v, float):
                return _fmt_num(v, digits=4)
            return str(v)
    return "—"


def render_cells_table(cells: list[dict[str, Any]]) -> str:
    header = "| Cell | Env | Reward | Err | Key metric | n | Wall (s) | Roll (s) | Tokens |"
    sep = "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"
    rows = [header, sep]
    for c in sorted(cells, key=lambda x: (x.get("harness", ""), x.get("feedback", ""), x.get("slug", ""))):
        wall_ms = float(c.get("wall_time_ms") or 0.0)
        roll_ms = c.get("rollout_time_ms_sum")
        roll_s = float(roll_ms) / 1000.0 if roll_ms is not None else None
        metrics = dict(c.get("avg_metrics") or {})
        tot = c.get("total_tokens")
        tok = _fmt_int(tot) if tot is not None else "—"
        rows.append(
            "| "
            + " | ".join(
                [
                    f"`{c.get('slug', '')}`",
                    f"`{c.get('env_id', '')}`",
                    _fmt_num(float(c.get("avg_reward", 0.0))),
                    _fmt_num(float(c.get("avg_error", 0.0))),
                    _key_metric(metrics),
                    str(int(c.get("num_rollouts", 0))),
                    _fmt_num(wall_ms / 1000.0, digits=1),
                    _fmt_num(roll_s, digits=1) if roll_s is not None else "—",
                    tok,
                ]
            )
            + " |"
        )
    return "\n".join(rows)


def render_run_report_markdown(
    run_dir: Path,
    payload: dict[str, Any],
    *,
    generated_at_utc: datetime | None = None,
) -> str:
    """Build a short REPORT.md from a ``summary.json``-shaped dict (no paths)."""
    run_dir = run_dir.resolve()
    spec = payload.get("spec") or {}
    cells = payload.get("cells") or []
    exp_name = run_dir.parent.name
    run_id = run_dir.name
    benchmark = _benchmark_label(exp_name)
    when = generated_at_utc or datetime.now(timezone.utc)
    when_s = when.strftime("%Y-%m-%d %H:%M UTC")

    return "\n".join(
        [
            f"# {exp_name} · {run_id}",
            "",
            f"**Benchmark:** {benchmark}",
            "",
            f"*{when_s}*",
            "",
            "## Config",
            "",
            f"```json\n{json.dumps(spec, indent=2)}\n```",
            "",
            "## Results",
            "",
            render_cells_table(cells),
            "",
        ]
    )


def write_run_report_md_from_payload(run_dir: Path, payload: dict[str, Any]) -> Path:
    """Write ``REPORT.md`` next to ``summary.json``."""
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    out = run_dir / "REPORT.md"
    out.write_text(render_run_report_markdown(run_dir, payload), encoding="utf-8")
    return out


def load_summary_and_write_report(run_dir: Path) -> Path:
    """Load ``summary.json`` under ``run_dir`` and write ``REPORT.md``."""
    run_dir = Path(run_dir)
    summary_path = run_dir / "summary.json"
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    return write_run_report_md_from_payload(run_dir, payload)


def find_summary_files(root: Path) -> list[Path]:
    """Return every ``summary.json`` under ``root`` (e.g. ``outputs/experiments``)."""
    root = Path(root)
    if not root.is_dir():
        return []
    return sorted(root.rglob("summary.json"))


def regenerate_all_reports(root: Path) -> list[Path]:
    """Rewrite ``REPORT.md`` for every run that has ``summary.json``."""
    written: list[Path] = []
    for summary_path in find_summary_files(root):
        written.append(load_summary_and_write_report(summary_path.parent))
    return written
