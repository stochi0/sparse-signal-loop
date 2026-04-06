from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Phase0Harness(str, Enum):
    """``chat`` = LongBench-Pro multi-turn chat loop; ``rlm`` = REPL recursive harness."""

    CHAT = "chat"
    RLM = "rlm"


class Phase0Feedback(str, Enum):
    """Judge feedback format after ``NO`` (see ``longbenchpro_prompts``)."""

    TOTAL_SCORE = "total_score"
    SINGLE_CRITERION = "single_criterion"


@dataclass(frozen=True)
class Phase0Cell:
    harness: Phase0Harness
    feedback: Phase0Feedback

    def slug(self) -> str:
        return f"{self.harness.value}__{self.feedback.value}"

    @staticmethod
    def factorial_design() -> list[Phase0Cell]:
        return [
            Phase0Cell(h, f)
            for h in (Phase0Harness.CHAT, Phase0Harness.RLM)
            for f in (Phase0Feedback.TOTAL_SCORE, Phase0Feedback.SINGLE_CRITERION)
        ]


@dataclass
class Phase0Spec:
    """Shared knobs across all four cells (keep identical except harness-specific limits)."""

    model: str = "openai/gpt-4.1-mini"
    judge_model: str = "openai/gpt-4.1-mini"
    num_examples: int = 1
    rollouts_per_example: int = 1
    max_concurrent: int = 2
    num_workers: int | str = "auto"
    seed: int | None = 42
    language: str = "English"
    dataset_start_index: int = 0
    token_length: str = "all"
    difficulty: str = "Moderate"
    thinking: bool = False
    include_env_tips: bool = False
    prompt_in_context_file: bool = False
    max_turns_chat: int = 8
    max_turns_rlm: int = 30
    max_judge_submissions: int = 8
    env_dir_path: str = "./environments"
    api_key_var: str = "PRIME_API_KEY"
    api_base_url: str = "https://api.pinference.ai/api/v1"
    client_type: str = "openai_chat_completions"
    judge_sampling_args: dict[str, Any] = field(default_factory=lambda: {"temperature": 0.0})
    sampling_args: dict[str, Any] = field(default_factory=dict)
    verbose: bool = False
    debug: bool = True
    save_results: bool = True
    max_retries: int = 0
    shuffle: bool = False
