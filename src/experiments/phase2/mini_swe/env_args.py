from __future__ import annotations

from typing import Any

from experiments.phase0.mini_swe.env_args import build_env_args as build_phase0_ms_env_args
from experiments.phase0.mini_swe.env_args import env_id_for_cell as env_id_phase0_ms
from experiments.phase0.schema import Phase0Cell
from experiments.phase2.schema import Phase2Cell, Phase2SkillArm

from .schema import Phase2MiniSweSpec


def env_id_for_cell(cell: Phase2Cell) -> str:
    return env_id_phase0_ms(Phase0Cell(harness=cell.harness, feedback=cell.feedback))


def _phase2_mode_for_arm(arm: Phase2SkillArm) -> str:
    return arm.value


def build_env_args(cell: Phase2Cell, spec: Phase2MiniSweSpec) -> dict[str, Any]:
    """Merge Phase 0 mini SWE kwargs with Phase 1 slice + Phase 2 skill harness."""
    p0 = Phase0Cell(harness=cell.harness, feedback=cell.feedback)
    base = build_phase0_ms_env_args(p0, spec)
    base["phase1_slice"] = bool(spec.phase1_slice)
    base["phase1_working_memory"] = "off"
    base["only_repos"] = spec.only_repos
    base["phase2_skill_mode"] = _phase2_mode_for_arm(cell.arm)
    base["phase2_skill_max_chars"] = int(spec.phase2_skill_max_chars)
    return base

