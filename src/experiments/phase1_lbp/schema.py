from __future__ import annotations

from dataclasses import dataclass

from experiments.phase0_lbp.schema import Phase0Spec


@dataclass
class Phase1LbpSpec(Phase0Spec):
    """Extends Phase 0 LBP spec with Phase 1 dataset slice (env defaults T6.1 @ 32k when slice is on)."""

    phase1_slice: bool = True
