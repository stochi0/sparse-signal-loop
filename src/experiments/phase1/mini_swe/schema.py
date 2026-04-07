from __future__ import annotations

from dataclasses import dataclass

from experiments.common.mini_swe_schema import MiniSweBaseSpec


@dataclass
class Phase1MiniSweSpec(MiniSweBaseSpec):
    """Extends Phase 0 mini SWE spec with Phase 1 slice + optional ``only_repos`` allow-list."""

    phase1_slice: bool = True
    only_repos: list[str] | None = None
