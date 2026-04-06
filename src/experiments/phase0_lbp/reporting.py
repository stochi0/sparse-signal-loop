from __future__ import annotations

from dataclasses import asdict, dataclass, field
from statistics import median
from typing import Any

from verifiers.types import GenerateMetadata, GenerateOutputs, RolloutOutput

# Rounds proxy: multiturn chat uses ``num_turns``; RLM uses ``root_llm_turns`` (REPL root calls).
DEFAULT_SUCCESS_K: tuple[int, ...] = (1, 2, 4, 8)


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


def _metric_value(o: RolloutOutput, name: str) -> float | None:
    """Read rubric metric from ``metrics`` or top-level (verifiers flattens metrics onto the output)."""
    m = o.get("metrics")
    if isinstance(m, dict):
        v = m.get(name)
        if isinstance(v, (int, float)):
            return float(v)
    v2 = o.get(name)
    if isinstance(v2, (int, float)):
        return float(v2)
    return None


def _rollout_rounds(o: RolloutOutput) -> int | None:
    for key in ("num_turns", "root_llm_turns"):
        v = _metric_value(o, key)
        if v is not None:
            return max(0, int(round(v)))
    return None


def _rollout_total_tokens(o: RolloutOutput) -> float | None:
    tu = o.get("token_usage")
    if not isinstance(tu, dict):
        return None
    inp = float(tu.get("input_tokens", 0) or 0)
    out = float(tu.get("output_tokens", 0) or 0)
    if inp == 0.0 and out == 0.0:
        return None
    return inp + out


def analyze_rollouts(
    outputs: list[RolloutOutput],
    *,
    success_k: tuple[int, ...] = DEFAULT_SUCCESS_K,
) -> dict[str, Any]:
    """Per-cell derived stats: judge YES rate, tokens-to-success, success@K (round-limited)."""
    n = len(outputs)
    task_vals: list[float] = []
    tokens_on_success: list[float] = []

    judge_per_rollout: list[float | None] = [_metric_value(o, "judge_reward") for o in outputs]
    judge_complete = n > 0 and all(j is not None for j in judge_per_rollout)
    judge_yes_rate: float | None = None
    if judge_complete:
        jv = [float(j) for j in judge_per_rollout]
        judge_yes_rate = sum(jv) / n

    for o in outputs:
        tm = _metric_value(o, "task_metric_reward")
        if tm is not None:
            task_vals.append(tm)
        j = _metric_value(o, "judge_reward")
        if j is not None and j >= 0.5:
            tt = _rollout_total_tokens(o)
            if tt is not None:
                tokens_on_success.append(tt)

    avg_task_metric_rollout = sum(task_vals) / len(task_vals) if task_vals else None

    mean_tokens_success = sum(tokens_on_success) / len(tokens_on_success) if tokens_on_success else None
    median_tokens_success = median(tokens_on_success) if tokens_on_success else None

    success_at_k: dict[str, float] = {}
    if judge_complete:
        for k in success_k:
            num = 0
            for o in outputs:
                j = _metric_value(o, "judge_reward")
                if j is None or j < 0.5:
                    continue
                r = _rollout_rounds(o)
                if r is not None and r <= k:
                    num += 1
            success_at_k[f"@{k}"] = num / n
    else:
        for k in success_k:
            success_at_k[f"@{k}"] = float("nan")

    return {
        "judge_yes_rate": judge_yes_rate,
        "avg_task_metric_rollout": avg_task_metric_rollout,
        "mean_tokens_success": mean_tokens_success,
        "median_tokens_success": median_tokens_success,
        "n_judge_success": len(tokens_on_success),
        "success_at_k": success_at_k,
    }


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
    judge_yes_rate: float | None = None
    avg_task_metric: float | None = None
    mean_tokens_success: float | None = None
    median_tokens_success: float | None = None
    n_judge_success: int = 0
    success_at_k: dict[str, float] = field(default_factory=dict)
    memory: str | None = None

    def to_json_dict(self) -> dict[str, Any]:
        d = asdict(self)
        return d


def summarize_cell(
    cell_slug: str,
    harness: str,
    feedback: str,
    env_id: str,
    outputs: GenerateOutputs,
    *,
    memory: str | None = None,
) -> Phase0CellSummary:
    meta: GenerateMetadata = outputs["metadata"]
    path = meta.get("path_to_save")
    path_s = str(path) if path is not None else None
    outs = outputs["outputs"]
    usage_dict = _usage_to_dict(meta.get("usage"))
    inp_t, out_t, tot_t = resolve_token_counts(usage_dict, outs)
    derived = analyze_rollouts(outs)
    avg_metrics = dict(meta.get("avg_metrics") or {})
    task_from_meta = avg_metrics.get("task_metric_reward")
    avg_task_metric: float | None
    if task_from_meta is not None:
        avg_task_metric = float(task_from_meta)
    else:
        avg_task_metric = derived["avg_task_metric_rollout"]
    return Phase0CellSummary(
        harness=harness,
        feedback=feedback,
        slug=cell_slug,
        env_id=env_id,
        avg_reward=float(meta.get("avg_reward", 0.0)),
        avg_metrics=avg_metrics,
        avg_error=float(meta.get("avg_error", 0.0)),
        wall_time_ms=float(meta.get("time_ms", 0.0)),
        rollout_time_ms_sum=_rollup_rollout_timing_ms(outs),
        input_tokens=inp_t,
        output_tokens=out_t,
        total_tokens=tot_t,
        usage=usage_dict,
        results_path=path_s,
        num_rollouts=len(outs),
        judge_yes_rate=derived["judge_yes_rate"],
        avg_task_metric=avg_task_metric,
        mean_tokens_success=derived["mean_tokens_success"],
        median_tokens_success=derived["median_tokens_success"],
        n_judge_success=int(derived["n_judge_success"]),
        success_at_k=dict(derived["success_at_k"]),
        memory=memory,
    )


def _fmt_rate(x: float | None, *, digits: int = 4) -> str:
    if x is None:
        return "n/a"
    if x != x:  # NaN
        return "n/a"
    return f"{x:.{digits}f}"


def _fmt_tokens_succ_mean(r: Phase0CellSummary) -> str:
    m = r.mean_tokens_success
    if m is None:
        return "n/a"
    return f"{m:.0f}"


def _fmt_tokens_succ_median(r: Phase0CellSummary) -> str:
    m = r.median_tokens_success
    if m is None:
        return "n/a"
    return f"{m:.0f}"


def print_comparison_table(rows: list[Phase0CellSummary]) -> None:
    """Stdout table for quick factorial inspection (optional ``memory`` column for Phase 1)."""
    ks = sorted({k for r in rows for k in r.success_at_k.keys()}, key=lambda s: int(s.lstrip("@")))
    k_headers = "".join(f"{k:>7}" for k in ks) if ks else ""
    show_mem = any(r.memory for r in rows)
    mem_h = f" {'mem':>8}" if show_mem else ""
    header = (
        f"{'cell':<36}{mem_h} {'judge':>8} {'reward':>8} {'task_m':>8}{k_headers} "
        f"{'tok_ok_mn':>10} {'tok_ok_md':>10} {'wall_s':>8} {'roll_s':>8} {'tok_tot':>10}"
    )
    print(header)
    print("-" * len(header))
    for r in sorted(rows, key=lambda x: (x.harness, x.feedback, x.memory or "")):
        jyr = r.judge_yes_rate
        judge_s = _fmt_rate(jyr)
        tm = r.avg_task_metric
        if tm is None:
            tm = r.avg_metrics.get("task_metric_reward")
        task_s = _fmt_rate(float(tm) if tm is not None else None)
        s_k = "".join(f"{_fmt_rate(r.success_at_k.get(k)):>7}" for k in ks) if ks else ""
        wall_s = r.wall_time_ms / 1000.0
        roll_sum = r.rollout_time_ms_sum
        roll_s_str = f"{roll_sum / 1000.0:.1f}" if roll_sum is not None else "n/a"
        ttot = f"{r.total_tokens:.0f}" if r.total_tokens is not None else "n/a"
        tok_m = _fmt_tokens_succ_mean(r)
        tok_med = _fmt_tokens_succ_median(r)
        mem_c = f" {r.memory or '—':>8}" if show_mem else ""
        print(
            f"{r.slug:<36}{mem_c} {judge_s:>8} {r.avg_reward:8.4f} {task_s:>8}{s_k} "
            f"{tok_m:>9} {tok_med:>10} {wall_s:8.1f} {roll_s_str:>8} {ttot:>10}"
        )
