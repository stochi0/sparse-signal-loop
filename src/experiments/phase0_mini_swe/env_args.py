from __future__ import annotations

from typing import Any

from experiments.phase0_lbp.schema import Phase0Cell, Phase0Harness
from experiments.phase0_mini_swe.schema import MiniSwePhase0Spec


def env_id_for_cell(cell: Phase0Cell) -> str:
    return "mini-swe-agent-plus" if cell.harness is Phase0Harness.CHAT else "mini-swe-agent-plus-rlm"


def build_env_args(cell: Phase0Cell, spec: MiniSwePhase0Spec) -> dict[str, Any]:
    """Keyword args for ``mini_swe_agent_plus`` / ``mini_swe_agent_plus_rlm`` ``load_environment``."""
    base: dict[str, Any] = {
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
    if cell.harness is Phase0Harness.CHAT:
        base["skip_swebench_install"] = spec.skip_swebench_install
    return base
