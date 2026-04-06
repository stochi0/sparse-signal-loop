from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from experiments.phase0.schema import Phase0Feedback, Phase0Harness


class Phase2SkillArm(str, Enum):
    """Which persistent / pseudo-persistent skill mechanism is active (paired with harness)."""

    RLM_SKILL_FILE = "rlm_skill_file"
    CHAT_NO_FILE = "chat_no_file"
    CHAT_SYSTEM_REINJECT = "chat_system_reinject"


@dataclass(frozen=True)
class Phase2Cell:
    """Phase 2 grid: RLM + ``SKILL.md`` vs chat without file vs chat with tag reinject × judge feedback."""

    harness: Phase0Harness
    feedback: Phase0Feedback
    arm: Phase2SkillArm

    def slug(self) -> str:
        return f"{self.harness.value}__{self.feedback.value}__{self.arm.value}"

    @staticmethod
    def factorial_design() -> list[Phase2Cell]:
        """Six cells: 3 arms × 2 judge feedback modes (arm implies harness)."""
        out: list[Phase2Cell] = []
        for f in (Phase0Feedback.TOTAL_SCORE, Phase0Feedback.SINGLE_CRITERION):
            out.append(Phase2Cell(Phase0Harness.RLM, f, Phase2SkillArm.RLM_SKILL_FILE))
            out.append(Phase2Cell(Phase0Harness.CHAT, f, Phase2SkillArm.CHAT_NO_FILE))
            out.append(Phase2Cell(Phase0Harness.CHAT, f, Phase2SkillArm.CHAT_SYSTEM_REINJECT))
        return out
