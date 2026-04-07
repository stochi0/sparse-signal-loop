from __future__ import annotations

from dataclasses import dataclass

from experiments.common.mini_swe_schema import MiniSweBaseSpec


@dataclass
class Phase2MiniSweSpec(MiniSweBaseSpec):
    """Phase 2 knobs for mini SWE (Phase 1 slice + Phase 2 skill harness)."""

    phase1_slice: bool = True
    only_repos: list[str] | None = None
    phase2_skill_max_chars: int = 6000

