"""Phase 1 (and similar grids): summarize RLM vs chat on the same judge-feedback axis."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Any

from experiments.kit.reporting import CellRunSummary


def _is_finite(x: float | None) -> bool:
    return x is not None and x == x


@dataclass(frozen=True)
class FeedbackHarnessContrast:
    """One row: same ``feedback`` mode, chat vs RLM memory arms."""

    feedback: str
    chat_judge_yes: float | None
    chat_reward: float | None
    rlm_mem_chat_judge_yes: float | None
    rlm_mem_chat_reward: float | None
    rlm_mem_repl_judge_yes: float | None
    rlm_mem_repl_reward: float | None

    @property
    def rlm_judge_yes_values(self) -> list[float]:
        out: list[float] = []
        for v in (self.rlm_mem_chat_judge_yes, self.rlm_mem_repl_judge_yes):
            if _is_finite(v):
                out.append(float(v))
        return out

    @property
    def rlm_reward_values(self) -> list[float]:
        out: list[float] = []
        for v in (self.rlm_mem_chat_reward, self.rlm_mem_repl_reward):
            if _is_finite(v):
                out.append(float(v))
        return out

    @property
    def delta_judge_yes_best_rlm_minus_chat(self) -> float | None:
        if not _is_finite(self.chat_judge_yes) or not self.rlm_judge_yes_values:
            return None
        return max(self.rlm_judge_yes_values) - float(self.chat_judge_yes)

    @property
    def delta_judge_yes_mean_rlm_minus_chat(self) -> float | None:
        if not _is_finite(self.chat_judge_yes) or not self.rlm_judge_yes_values:
            return None
        return mean(self.rlm_judge_yes_values) - float(self.chat_judge_yes)

    @property
    def delta_reward_best_rlm_minus_chat(self) -> float | None:
        if not _is_finite(self.chat_reward) or not self.rlm_reward_values:
            return None
        return max(self.rlm_reward_values) - float(self.chat_reward)

    @property
    def delta_reward_mean_rlm_minus_chat(self) -> float | None:
        if not _is_finite(self.chat_reward) or not self.rlm_reward_values:
            return None
        return mean(self.rlm_reward_values) - float(self.chat_reward)


def build_phase1_harness_contrast(rows: list[CellRunSummary]) -> list[FeedbackHarnessContrast]:
    """Group Phase 1 cells by judge feedback; fill chat + RLM×memory slots when present."""
    if not rows:
        return []

    by_fb: dict[str, dict[str, CellRunSummary]] = {}
    for r in rows:
        if not r.memory:
            continue
        by_fb.setdefault(r.feedback, {})[f"{r.harness}:{r.memory}"] = r

    out: list[FeedbackHarnessContrast] = []
    for fb in sorted(by_fb.keys()):
        m = by_fb[fb]
        chat = m.get("chat:chat")
        rlm_mc = m.get("rlm:chat")
        rlm_rf = m.get("rlm:repl_files")
        out.append(
            FeedbackHarnessContrast(
                feedback=fb,
                chat_judge_yes=chat.judge_yes_rate if chat else None,
                chat_reward=chat.avg_reward if chat else None,
                rlm_mem_chat_judge_yes=rlm_mc.judge_yes_rate if rlm_mc else None,
                rlm_mem_chat_reward=rlm_mc.avg_reward if rlm_mc else None,
                rlm_mem_repl_judge_yes=rlm_rf.judge_yes_rate if rlm_rf else None,
                rlm_mem_repl_reward=rlm_rf.avg_reward if rlm_rf else None,
            )
        )
    return out


def phase1_harness_contrast_applicable(rows: list[CellRunSummary]) -> bool:
    """True when we have Phase 1-style rows (memory set) and at least one chat vs RLM pair for some feedback."""
    if not any(r.memory for r in rows):
        return False
    contrasts = build_phase1_harness_contrast(rows)
    for c in contrasts:
        if _is_finite(c.chat_judge_yes) and c.rlm_judge_yes_values:
            return True
        if _is_finite(c.chat_reward) and c.rlm_reward_values:
            return True
    return False


def _fmt_delta(x: float | None) -> str:
    if x is None:
        return "n/a"
    if x != x:
        return "n/a"
    sign = "+" if x > 0 else ""
    return f"{sign}{x:.4f}"


def _fmt_metric(x: float | None) -> str:
    if x is None or (isinstance(x, float) and x != x):
        return "n/a"
    return f"{x:.4f}"


def print_phase1_harness_contrast(rows: list[CellRunSummary]) -> None:
    """Stdout table: RLM vs chat per judge-feedback mode (positive Δ = RLM ahead on that metric)."""
    contrasts = build_phase1_harness_contrast(rows)
    if not contrasts:
        return
    if not phase1_harness_contrast_applicable(rows):
        print(
            "\n[RLM vs chat] No overlapping feedback rows with both chat and RLM; "
            "run full grid or pair cells with the same --feedback mode.\n"
        )
        return

    print("\n=== RLM vs chat (same judge feedback) ===")
    print(
        "Positive Δ = RLM ahead. 'best RLM' = max over RLM memory arms present; "
        "'mean RLM' = mean over those arms.\n"
    )
    hdr = (
        f"{'feedback':<20} {'chat_JY':>9} {'rlm_mc':>9} {'rlm_rf':>9} "
        f"{'ΔJY_best':>10} {'ΔJY_mean':>10} {'chat_rw':>9} {'Δrw_best':>10} {'Δrw_mean':>10}"
    )
    print(hdr)
    print("-" * len(hdr))
    for c in contrasts:
        if not _is_finite(c.chat_judge_yes) and not c.rlm_judge_yes_values:
            continue
        print(
            f"{c.feedback:<20} "
            f"{_fmt_metric(c.chat_judge_yes):>9} "
            f"{_fmt_metric(c.rlm_mem_chat_judge_yes):>9} "
            f"{_fmt_metric(c.rlm_mem_repl_judge_yes):>9} "
            f"{_fmt_delta(c.delta_judge_yes_best_rlm_minus_chat):>10} "
            f"{_fmt_delta(c.delta_judge_yes_mean_rlm_minus_chat):>10} "
            f"{_fmt_metric(c.chat_reward):>9} "
            f"{_fmt_delta(c.delta_reward_best_rlm_minus_chat):>10} "
            f"{_fmt_delta(c.delta_reward_mean_rlm_minus_chat):>10}"
        )
    print()


def render_phase1_harness_contrast_markdown(rows: list[dict[str, Any]]) -> str | None:
    """Markdown section for REPORT.md from ``summary.json`` cell dicts."""
    summaries = [_cell_dict_to_summary(c) for c in rows]
    if not phase1_harness_contrast_applicable(summaries):
        return None
    contrasts = build_phase1_harness_contrast(summaries)
    lines = [
        "## RLM vs chat (matched judge feedback)",
        "",
        "Within each **feedback** column from the factorial, **chat** is the non-RLM loop; **rlm_mc** / **rlm_rf** are "
        "RLM with working memory in chat vs REPL files. **Δ** columns are RLM − chat (positive ⇒ RLM higher). "
        "**best** uses the stronger RLM arm; **mean** averages RLM arms that were run.",
        "",
        "| Judge feedback | Chat JY | RLM JY (mem chat) | RLM JY (mem repl) | Δ JY best | Δ JY mean | "
        "Chat reward | Δ rw best | Δ rw mean |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for c in contrasts:
        if not _is_finite(c.chat_judge_yes) and not c.rlm_judge_yes_values:
            continue
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{c.feedback}`",
                    _fmt_metric(c.chat_judge_yes),
                    _fmt_metric(c.rlm_mem_chat_judge_yes),
                    _fmt_metric(c.rlm_mem_repl_judge_yes),
                    _fmt_delta(c.delta_judge_yes_best_rlm_minus_chat),
                    _fmt_delta(c.delta_judge_yes_mean_rlm_minus_chat),
                    _fmt_metric(c.chat_reward),
                    _fmt_delta(c.delta_reward_best_rlm_minus_chat),
                    _fmt_delta(c.delta_reward_mean_rlm_minus_chat),
                ]
            )
            + " |"
        )
    lines.append("")
    return "\n".join(lines)


def _float_opt(c: dict[str, Any], key: str) -> float | None:
    v = c.get(key)
    if v is None:
        return None
    if isinstance(v, (int, float)):
        x = float(v)
        return None if x != x else x
    return None


def _cell_dict_to_summary(c: dict[str, Any]) -> CellRunSummary:
    """Minimal reconstruction for contrast logic (only fields we read)."""
    sak_raw = c.get("success_at_k")
    sak: dict[str, float] = {}
    if isinstance(sak_raw, dict):
        for k, v in sak_raw.items():
            if isinstance(v, (int, float)):
                fv = float(v)
                if fv == fv:
                    sak[str(k)] = fv
    am = c.get("avg_metrics")
    avg_metrics: dict[str, float] = {}
    if isinstance(am, dict):
        for k, v in am.items():
            if isinstance(v, (int, float)):
                fv = float(v)
                if fv == fv:
                    avg_metrics[str(k)] = fv
    mem = c.get("memory")
    sk = c.get("skill_arm")
    return CellRunSummary(
        harness=str(c.get("harness", "")),
        feedback=str(c.get("feedback", "")),
        slug=str(c.get("slug", "")),
        env_id=str(c.get("env_id", "")),
        avg_reward=float(c.get("avg_reward") or 0.0),
        avg_metrics=avg_metrics,
        avg_error=float(c.get("avg_error") or 0.0),
        wall_time_ms=float(c.get("wall_time_ms") or 0.0),
        rollout_time_ms_sum=_float_opt(c, "rollout_time_ms_sum"),
        input_tokens=_float_opt(c, "input_tokens"),
        output_tokens=_float_opt(c, "output_tokens"),
        total_tokens=_float_opt(c, "total_tokens"),
        usage=dict(c["usage"]) if isinstance(c.get("usage"), dict) else None,
        results_path=str(c["results_path"]) if c.get("results_path") is not None else None,
        num_rollouts=int(c.get("num_rollouts") or 0),
        judge_yes_rate=_float_opt(c, "judge_yes_rate"),
        avg_task_metric=_float_opt(c, "avg_task_metric"),
        mean_tokens_success=_float_opt(c, "mean_tokens_success"),
        median_tokens_success=_float_opt(c, "median_tokens_success"),
        n_judge_success=int(c.get("n_judge_success") or 0),
        success_at_k=sak,
        memory=str(mem) if mem is not None else None,
        skill_arm=str(sk) if sk is not None else None,
    )
