from __future__ import annotations

from typing import Any, Protocol

from experiments.common.schema import BaseCell, BaseHarness


class MiniSweSpecLike(Protocol):
    dataset_name: str
    dataset_start_index: int
    max_turns: int
    judge_model: str
    judge_sampling_args: dict[str, Any]
    max_judge_submissions: int
    allow_git: bool
    filter_repos: list[str] | None
    skip_swebench_install: bool


def env_id_for_harness(harness: BaseHarness) -> str:
    return "mini-swe-agent-plus" if harness is BaseHarness.CHAT else "mini-swe-agent-plus-rlm"


def build_base_env_args(cell: BaseCell, spec: MiniSweSpecLike) -> dict[str, Any]:
    """Keyword args for ``mini_swe_agent_plus`` / ``mini_swe_agent_plus_rlm`` ``load_environment``."""
    args: dict[str, Any] = {
        "dataset_name": spec.dataset_name,
        "dataset_start_index": spec.dataset_start_index,
        "max_turns": spec.max_turns,
        "judge_feedback_mode": cell.feedback.value,
        "in_loop_judge": True,
        "judge_model": spec.judge_model,
        "judge_sampling_args": dict(spec.judge_sampling_args),
        "max_judge_submissions": spec.max_judge_submissions,
        "allow_git": spec.allow_git,
        "filter_repos": spec.filter_repos,
    }
    if cell.harness is BaseHarness.CHAT:
        args["skip_swebench_install"] = spec.skip_swebench_install
    return args
