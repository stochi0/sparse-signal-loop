from __future__ import annotations

from dataclasses import dataclass

from experiments.phase0.schema import Phase0Spec


@dataclass
class Phase2LbpSpec(Phase0Spec):
    """LBP knobs for Phase 2 (Phase 1 slice pinning; Phase 1 working memory forced off in env_args)."""

    phase1_slice: bool = True
    phase2_skill_max_chars: int = 6000
