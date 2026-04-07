from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from experiments.common.schema import BaseFeedback, BaseHarness


class Phase1WorkingMemory(str, Enum):
    """Where Phase 1 checklist / hypothesis / failure log must live (see env ``phase1_working_memory``)."""

    CHAT = "chat"
    REPL_FILES = "repl_files"


@dataclass(frozen=True)
class Phase1Cell:
    """Phase 1 grid: chat harness (notes-in-chat only) vs RLM × {chat ablation, repl files} × judge feedback."""

    harness: BaseHarness
    feedback: BaseFeedback
    memory: Phase1WorkingMemory

    def slug(self) -> str:
        return f"{self.harness.value}__{self.feedback.value}__mem_{self.memory.value}"

    @staticmethod
    def factorial_design() -> list[Phase1Cell]:
        """Six cells: 2 (chat × feedback) + 4 (RLM × 2 memory × 2 feedback)."""
        out: list[Phase1Cell] = []
        for f in (BaseFeedback.TOTAL_SCORE, BaseFeedback.SINGLE_CRITERION):
            out.append(Phase1Cell(BaseHarness.CHAT, f, Phase1WorkingMemory.CHAT))
        for f in (BaseFeedback.TOTAL_SCORE, BaseFeedback.SINGLE_CRITERION):
            out.append(Phase1Cell(BaseHarness.RLM, f, Phase1WorkingMemory.CHAT))
            out.append(Phase1Cell(BaseHarness.RLM, f, Phase1WorkingMemory.REPL_FILES))
        return out
