from __future__ import annotations

from typing import Any

from experiments.phase0.lbp.env_args import build_env_args as build_phase0_lbp_env_args
from experiments.phase0.schema import Phase0Cell, Phase0Harness
from experiments.phase2.schema import Phase2Cell, Phase2SkillArm

from .schema import Phase2LbpSpec


def env_id_for_cell(cell: Phase2Cell) -> str:
    return "longbenchpro" if cell.harness is Phase0Harness.CHAT else "longbenchpro-rlm"


def _phase2_mode_for_arm(arm: Phase2SkillArm) -> str:
    return arm.value


def build_env_args(cell: Phase2Cell, spec: Phase2LbpSpec) -> dict[str, Any]:
    """Merge Phase 0 LBP kwargs with Phase 2 skill harness (Phase 1 working memory off)."""
    p0 = Phase0Cell(harness=cell.harness, feedback=cell.feedback)
    base = build_phase0_lbp_env_args(p0, spec)
    base["phase1_working_memory"] = "off"
    base["phase1_slice"] = spec.phase1_slice
    base["phase2_skill_mode"] = _phase2_mode_for_arm(cell.arm)
    base["phase2_skill_max_chars"] = int(spec.phase2_skill_max_chars)
    return base
