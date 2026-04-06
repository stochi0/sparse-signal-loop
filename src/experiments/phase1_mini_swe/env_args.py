from __future__ import annotations

from typing import Any

from experiments.phase0_lbp.schema import Phase0Cell
from experiments.phase0_mini_swe.env_args import build_env_args as build_phase0_ms_env_args
from experiments.phase0_mini_swe.env_args import env_id_for_cell as env_id_phase0_ms
from experiments.phase1_common.schema import Phase1Cell, Phase1WorkingMemory

from .schema import Phase1MiniSweSpec


def env_id_for_cell(cell: Phase1Cell) -> str:
    return env_id_phase0_ms(Phase0Cell(harness=cell.harness, feedback=cell.feedback))


def build_env_args(cell: Phase1Cell, spec: Phase1MiniSweSpec) -> dict[str, Any]:
    p0 = Phase0Cell(harness=cell.harness, feedback=cell.feedback)
    base = build_phase0_ms_env_args(p0, spec)
    wm = "chat" if cell.memory is Phase1WorkingMemory.CHAT else "repl_files"
    base["phase1_slice"] = spec.phase1_slice
    base["phase1_working_memory"] = wm
    base["only_repos"] = spec.only_repos
    return base
