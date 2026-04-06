from __future__ import annotations

from dataclasses import dataclass

from experiments.phase0.schema import Phase0Spec


@dataclass
class Phase2LbpSpec(Phase0Spec):
    """LBP knobs for Phase 2 (Phase 1 slice pinning; Phase 1 working memory forced off in env_args)."""

    phase1_slice: bool = True
    phase2_skill_max_chars: int = 6000
    # Forwarded to ``longbenchpro_rlm`` only (ignored for chat cells).
    rlm_sandbox_cpu_cores: int | None = None
    rlm_sandbox_memory_gb: int | None = None
    rlm_sandbox_disk_size_gb: int | None = None
    rlm_sandbox_timeout_minutes: int | None = None
    rlm_code_execution_timeout: int | None = None
    rlm_sub_llm_max_turns: int | None = None
