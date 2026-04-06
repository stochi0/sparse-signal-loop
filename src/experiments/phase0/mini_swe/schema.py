from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

DatasetName = Literal[
    "R2E-Gym/R2E-Gym-Subset",
    "SWE-bench/SWE-bench_Verified",
    "PrimeIntellect/SWE-Bench-Verified-Quick",
]


@dataclass
class MiniSwePhase0Spec:
    """Shared knobs for all four MSAP factorial cells."""

    model: str = "openai/gpt-4.1-mini"
    judge_model: str = "openai/gpt-4.1-mini"
    num_examples: int = 1
    rollouts_per_example: int = 1
    max_concurrent: int = 1
    num_workers: int | str = "auto"
    dataset_name: DatasetName = "PrimeIntellect/SWE-Bench-Verified-Quick"
    dataset_start_index: int = 0
    max_turns: int = 80
    max_judge_submissions: int = 8
    filter_repos: list[str] | None = None
    allow_git: bool = False
    skip_swebench_install: bool = True
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
