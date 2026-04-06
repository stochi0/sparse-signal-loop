from __future__ import annotations

from typing import Any

from experiments.phase0.schema import Phase0Cell, Phase0Harness, Phase0Spec


def env_id_for_cell(cell: Phase0Cell) -> str:
    return "longbenchpro" if cell.harness is Phase0Harness.CHAT else "longbenchpro-rlm"


def build_env_args(cell: Phase0Cell, spec: Phase0Spec) -> dict[str, Any]:
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
    if cell.harness is Phase0Harness.CHAT:
        args["max_turns"] = spec.max_turns_chat
    else:
        args["max_turns"] = spec.max_turns_rlm
        args["max_judge_submissions"] = spec.max_judge_submissions
    return args
