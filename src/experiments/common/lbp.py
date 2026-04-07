from __future__ import annotations

from typing import Any, Protocol

from experiments.common.schema import BaseCell, BaseHarness


class LbpSpecLike(Protocol):
    judge_model: str
    judge_sampling_args: dict[str, Any]
    shuffle: bool
    seed: int | None
    language: str
    dataset_start_index: int
    token_length: str
    difficulty: str
    thinking: bool
    include_env_tips: bool
    prompt_in_context_file: bool
    max_turns_chat: int
    max_turns_rlm: int
    max_judge_submissions: int


def env_id_for_harness(harness: BaseHarness) -> str:
    return "longbenchpro" if harness is BaseHarness.CHAT else "longbenchpro-rlm"


def build_base_env_args(cell: BaseCell, spec: LbpSpecLike) -> dict[str, Any]:
    """Keyword args for ``longbenchpro`` / ``longbenchpro_rlm`` ``load_environment``."""
    args: dict[str, Any] = {
        "judge_feedback_mode": cell.feedback.value,
        "in_loop_judge": True,
        "judge_model": spec.judge_model,
        "judge_sampling_args": dict(spec.judge_sampling_args),
        "shuffle": spec.shuffle,
        "seed": spec.seed if spec.shuffle else None,
        "language": spec.language,
        "dataset_start_index": spec.dataset_start_index,
        "token_length": spec.token_length,
        "difficulty": spec.difficulty,
        "thinking": spec.thinking,
        "include_env_tips": spec.include_env_tips,
        "prompt_in_context_file": spec.prompt_in_context_file,
    }
    if cell.harness is BaseHarness.CHAT:
        args["max_turns"] = spec.max_turns_chat
    else:
        args["max_turns"] = spec.max_turns_rlm
        args["max_judge_submissions"] = spec.max_judge_submissions
    return args
