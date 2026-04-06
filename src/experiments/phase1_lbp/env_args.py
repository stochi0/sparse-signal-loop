from __future__ import annotations

from typing import Any

from experiments.phase0_lbp.env_args import build_env_args as build_phase0_lbp_env_args
from experiments.phase0_lbp.schema import Phase0Cell, Phase0Harness
from experiments.phase1_common.schema import Phase1Cell, Phase1WorkingMemory

from .schema import Phase1LbpSpec


def env_id_for_cell(cell: Phase1Cell) -> str:
    return "longbenchpro" if cell.harness is Phase0Harness.CHAT else "longbenchpro-rlm"


def build_env_args(cell: Phase1Cell, spec: Phase1LbpSpec) -> dict[str, Any]:
    """Merge Phase 0 LBP kwargs with ``phase1_slice`` / ``phase1_working_memory``."""
    p0 = Phase0Cell(harness=cell.harness, feedback=cell.feedback)
    base = build_phase0_lbp_env_args(p0, spec)
    wm = "chat" if cell.memory is Phase1WorkingMemory.CHAT else "repl_files"
    base["phase1_slice"] = spec.phase1_slice
    base["phase1_working_memory"] = wm
    return base
