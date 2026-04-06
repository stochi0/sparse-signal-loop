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
    if isinstance(x, float) and x != x:
        return na
    return f"{x:.{digits}f}"


def _fmt_int(x: float | None, na: str = "—") -> str:
    if x is None:
        return na
    return f"{int(round(x)):,}"


def _effective_judge_yes_rate(c: dict[str, Any], metrics: dict[str, Any]) -> float | None:
    j = c.get("judge_yes_rate")
    if j is not None:
        return float(j)
    jr = metrics.get("judge_reward")
    if isinstance(jr, (int, float)):
        return float(jr)
    return None


def _success_k_columns(cells: list[dict[str, Any]]) -> list[str]:
    keys: set[str] = set()
    for c in cells:
        sak = c.get("success_at_k")
        if isinstance(sak, dict):
            keys.update(sak.keys())
    return sorted(keys, key=lambda s: int(s.lstrip("@")))


def render_cells_table(cells: list[dict[str, Any]]) -> str:
    k_cols = _success_k_columns(cells)
    k_header = "".join(f" | {k}" for k in k_cols)
    k_sep = "".join(" | ---:" for _ in k_cols)
    header = (
        "| Cell | Env | Judge YES | Reward | Err | Task metric"
        + k_header
        + " | Mean tok (success) | Median tok (success) | n succ | n | Wall (s) | Roll (s) | Tokens |"
    )
    sep = (
        "| --- | --- | ---: | ---: | ---: | ---:"
        + k_sep
        + " | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"
    )
    rows = [header, sep]
    for c in sorted(cells, key=lambda x: (x.get("harness", ""), x.get("feedback", ""), x.get("slug", ""))):
        wall_ms = float(c.get("wall_time_ms") or 0.0)
        roll_ms = c.get("rollout_time_ms_sum")
        roll_s = float(roll_ms) / 1000.0 if roll_ms is not None else None
        metrics = dict(c.get("avg_metrics") or {})
        tot = c.get("total_tokens")
        tok = _fmt_int(tot) if tot is not None else "—"
        task_m = c.get("avg_task_metric")
        if task_m is None:
            task_m = metrics.get("task_metric_reward")
        sak_raw = c.get("success_at_k")
        sak_dict = sak_raw if isinstance(sak_raw, dict) else {}
        k_cells = [_fmt_num(sak_dict.get(k), digits=4) for k in k_cols]
        judge_yes = _effective_judge_yes_rate(c, metrics)
        mean_tok_s = c.get("mean_tokens_success")
        med_tok_s = c.get("median_tokens_success")
        n_succ = c.get("n_judge_success")
        rows.append(
            "| "
            + " | ".join(
                [
                    f"`{c.get('slug', '')}`",
                    f"`{c.get('env_id', '')}`",
                    _fmt_num(judge_yes, digits=4),
                    _fmt_num(float(c.get("avg_reward", 0.0))),
                    _fmt_num(float(c.get("avg_error", 0.0))),
                    _fmt_num(float(task_m) if task_m is not None else None, digits=4),
                    *k_cells,
                    _fmt_int(mean_tok_s) if mean_tok_s is not None else "—",
                    _fmt_int(med_tok_s) if med_tok_s is not None else "—",
                    str(int(n_succ)) if n_succ is not None else "—",
                    str(int(c.get("num_rollouts", 0))),
                    _fmt_num(wall_ms / 1000.0, digits=1),
                    _fmt_num(roll_s, digits=1) if roll_s is not None else "—",
                    tok,
                ]
            )
            + " |"
        )
    note = (
        "\n\n**Success@K** is the fraction of rollouts where the judge accepted (`judge_reward` ≥ 0.5) "
        "and round count ≤ K. Chat harness uses `num_turns` (assistant generations); "
        "RLM uses `root_llm_turns` (root REPL calls). "
        "**Mean tok (success)** / **Median tok (success)** aggregate total tokens (input + output) over "
        "judge-success rollouts when per-rollout `token_usage` is present (newer runs only; older "
        "`summary.json` files may leave these blank)."
    )
    return "\n".join(rows) + note


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
