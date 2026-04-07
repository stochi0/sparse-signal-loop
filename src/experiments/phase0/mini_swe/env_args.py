from __future__ import annotations

from typing import Any

from experiments.common.mini_swe import build_base_env_args, env_id_for_harness
from experiments.phase0.schema import Phase0Cell

from .schema import MiniSwePhase0Spec


def env_id_for_cell(cell: Phase0Cell) -> str:
    return env_id_for_harness(cell.harness)


def build_env_args(cell: Phase0Cell, spec: MiniSwePhase0Spec) -> dict[str, Any]:
    return build_base_env_args(cell, spec)
