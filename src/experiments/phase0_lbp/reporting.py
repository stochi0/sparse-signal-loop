from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from verifiers.types import GenerateMetadata, GenerateOutputs, RolloutOutput


def _usage_to_dict(usage: object | None) -> dict[str, Any] | None:
    if usage is None:
        return None
    if isinstance(usage, dict):
        return dict(usage)
    if hasattr(usage, "model_dump"):
        return usage.model_dump()
    return dict(usage)


def _token_fields_from_usage(usage: dict[str, Any] | None) -> tuple[float | None, float | None]:
    if not usage:
        return None, None
    inp = usage.get("input_tokens")
    out = usage.get("output_tokens")
    if inp is None and out is None:
        return None, None
    return float(inp or 0), float(out or 0)


def _rollup_tokens_from_rollouts(outputs: list[RolloutOutput]) -> tuple[float, float]:
    inp_t = out_t = 0.0
    for o in outputs:
        tu = o.get("token_usage")
        if isinstance(tu, dict):
            inp_t += float(tu.get("input_tokens", 0) or 0)
            out_t += float(tu.get("output_tokens", 0) or 0)
    return inp_t, out_t


def _rollup_rollout_timing_ms(outputs: list[RolloutOutput]) -> float | None:
    """Sum of per-rollout ``timing.total_ms`` when present (generation+scoring, not full queue wait)."""
    total = 0.0
    n = 0
    for o in outputs:
        timing = o.get("timing")
        if isinstance(timing, dict) and "total_ms" in timing:
            total += float(timing["total_ms"])
            n += 1
    return total if n else None


def resolve_token_counts(
    meta_usage: dict[str, Any] | None,
    outputs: list[RolloutOutput],
) -> tuple[float | None, float | None, float | None]:
    """Return (input_tokens, output_tokens, total_tokens). Prefer aggregate metadata; else sum rollouts."""
    in_m, out_m = _token_fields_from_usage(meta_usage)
    if in_m is not None or out_m is not None:
        i = in_m or 0.0
        o = out_m or 0.0
        tot = i + o
        if meta_usage and meta_usage.get("total_tokens") is not None:
            tot = max(tot, float(meta_usage["total_tokens"]))
        return i, o, tot
    ri, ro = _rollup_tokens_from_rollouts(outputs)
    if ri == 0.0 and ro == 0.0:
        return None, None, None
    return ri, ro, ri + ro


@dataclass
class Phase0CellSummary:
    harness: str
    feedback: str
    slug: str
    env_id: str
    avg_reward: float
    avg_metrics: dict[str, float]
    avg_error: float
    wall_time_ms: float
    rollout_time_ms_sum: float | None
    input_tokens: float | None
    output_tokens: float | None
    total_tokens: float | None
    usage: dict[str, Any] | None
    results_path: str | None
    num_rollouts: int

    def to_json_dict(self) -> dict[str, Any]:
        d = asdict(self)
        return d


def summarize_cell(
    cell_slug: str,
    harness: str,
    feedback: str,
    env_id: str,
    outputs: GenerateOutputs,
) -> Phase0CellSummary:
    meta: GenerateMetadata = outputs["metadata"]
    path = meta.get("path_to_save")
    path_s = str(path) if path is not None else None
    outs = outputs["outputs"]
    usage_dict = _usage_to_dict(meta.get("usage"))
    inp_t, out_t, tot_t = resolve_token_counts(usage_dict, outs)
    return Phase0CellSummary(
        harness=harness,
        feedback=feedback,
        slug=cell_slug,
        env_id=env_id,
        avg_reward=float(meta.get("avg_reward", 0.0)),
        avg_metrics=dict(meta.get("avg_metrics") or {}),
        avg_error=float(meta.get("avg_error", 0.0)),
        wall_time_ms=float(meta.get("time_ms", 0.0)),
        rollout_time_ms_sum=_rollup_rollout_timing_ms(outs),
        input_tokens=inp_t,
        output_tokens=out_t,
        total_tokens=tot_t,
        usage=usage_dict,
        results_path=path_s,
        num_rollouts=len(outs),
    )


def write_run_summary(run_dir: Path, spec_dict: dict[str, Any], rows: list[Phase0CellSummary]) -> Path:
    run_dir.mkdir(parents=True, exist_ok=True)
    out = run_dir / "summary.json"
    payload = {
        "spec": spec_dict,
        "cells": [r.to_json_dict() for r in rows],
    }
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return out


def print_comparison_table(rows: list[Phase0CellSummary]) -> None:
    """Stdout table for quick 2×2 inspection."""
    header = (
        f"{'cell':<36} {'reward':>8} {'task_m':>8} "
        f"{'wall_s':>8} {'roll_s':>8} {'tok_in':>10} {'tok_out':>10} {'tok_tot':>10}"
    )
    print(header)
    print("-" * len(header))
    for r in sorted(rows, key=lambda x: (x.harness, x.feedback)):
        tm = r.avg_metrics.get("task_metric_reward")
        task_s = f"{tm:.4f}" if tm is not None else "n/a"
        wall_s = r.wall_time_ms / 1000.0
        roll_sum = r.rollout_time_ms_sum
        roll_s_str = f"{roll_sum / 1000.0:.1f}" if roll_sum is not None else "n/a"
        tin = f"{r.input_tokens:.0f}" if r.input_tokens is not None else "n/a"
        tout = f"{r.output_tokens:.0f}" if r.output_tokens is not None else "n/a"
        ttot = f"{r.total_tokens:.0f}" if r.total_tokens is not None else "n/a"
        print(
            f"{r.slug:<36} {r.avg_reward:8.4f} {task_s:>8} "
            f"{wall_s:8.1f} {roll_s_str:>8} {tin:>10} {tout:>10} {ttot:>10}"
        )
