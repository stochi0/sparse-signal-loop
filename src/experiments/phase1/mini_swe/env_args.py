from __future__ import annotations

from typing import Any

from experiments.common.mini_swe import build_base_env_args, env_id_for_harness
from experiments.common.schema import BaseCell
from experiments.phase1.schema import Phase1Cell, Phase1WorkingMemory

from .schema import Phase1MiniSweSpec


def env_id_for_cell(cell: Phase1Cell) -> str:
    return env_id_for_harness(cell.harness)


def build_env_args(cell: Phase1Cell, spec: Phase1MiniSweSpec) -> dict[str, Any]:
    p0 = BaseCell(harness=cell.harness, feedback=cell.feedback)
    base = build_base_env_args(p0, spec)
    wm = "chat" if cell.memory is Phase1WorkingMemory.CHAT else "repl_files"
    base["phase1_slice"] = spec.phase1_slice
    base["phase1_working_memory"] = wm
    base["only_repos"] = spec.only_repos
    return base
