from __future__ import annotations

from dataclasses import dataclass

from experiments.phase0_mini_swe.schema import MiniSwePhase0Spec


@dataclass
class Phase1MiniSweSpec(MiniSwePhase0Spec):
    """Extends Phase 0 mini SWE spec with Phase 1 slice + optional ``only_repos`` allow-list."""

    phase1_slice: bool = True
    only_repos: list[str] | None = None
