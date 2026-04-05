"""LLM judge prompts for mini-swe-agent-plus (non-RLM, tool-loop).

Align wording with ``mini_swe_judge_prompts`` in the RLM package when changing behavior.
"""

from __future__ import annotations

from typing import Literal

JudgeFeedbackMode = Literal["freeform", "total_score", "single_criterion"]

ITERATIVE_JUDGE_INSTRUCTION_SUFFIX = """\n\n**Iterative judge:** When you submit with ``echo MINI_SWE_AGENT_FINAL_OUTPUT``, an LLM judge \
reviews your ``git diff`` (and any assistant text) against the task. If the first line of the judge response is NO, \
the tool output will include a ``--- Judge ---`` section with concise feedback — treat that as your guide, fix the \
code, and **submit again** with the same echo command. You can repeat until the judge accepts YES or you hit the \
wrong-submission limit. Leave enough turns before ``max_turns`` for at least one full reject→revise→resubmit cycle."""

SubmissionVariant = Literal["chat", "rlm"]

_SUBMISSION_LINE = {
    "chat": "Agent submission (final assistant message text, if any, plus repository diff):",
    "rlm": "Agent submission (declared final answer plus repository diff):",
}

_NO_FEEDBACK_RULES = """Strict rules for feedback after NO (all modes):
- Do NOT quote, paste, paraphrase, or walk through specific code lines from the reference patch, or disclose exact \
edits that are not already implied by the agent's diff.
- Do NOT reproduce the gold patch or "should be X instead of Y" when the correction comes only from the reference.
- DO give process guidance: which files or areas to re-check, tests to run, edge cases to consider, without teaching \
the solution."""


def _swe_intro(variant: SubmissionVariant) -> str:
    sub = _SUBMISSION_LINE[variant]
    return f"""You review a software-engineering rollout before hidden tests run.

Problem / PR description (what the agent must fix or implement):
```
{{question}}
```

Reference for grading (gold patch when available, plus problem context — do NOT quote or disclose patch lines in feedback to the agent):
```
{{answer}}
```

{sub}
```
{{response}}
```

Reply with exactly one word on the first line: YES if the diff and summary plausibly address the problem in a way \
consistent with the reference when a patch is shown; otherwise NO."""


_FREEFORM_BLOCK = f"""If the first line is NO, add one or more following lines with concise, actionable feedback \
(what to re-check, files, tests to run) without revealing specific solution code from the reference patch or exact \
line-by-line fixes.

{_NO_FEEDBACK_RULES}"""

_TOTAL_SCORE_BLOCK = f"""If the first line is NO, you must add the following lines after it (dense feedback):
1. Four lines, one per criterion, each exactly in this form (score must be 0 or 1 only):
   PROBLEM_FIT: <0 or 1> — <one short note; no reference-patch leakage>
   PATCH_QUALITY: <0 or 1> — <one short note>
   SCOPE: <0 or 1> — <one short note>
   VERIFICATION: <0 or 1> — <one short note>
   Definitions: PROBLEM_FIT = change targets the described issue / PR intent; PATCH_QUALITY = plausible, not obviously \
broken; SCOPE = reasonably targeted, not gratuitous unrelated churn; VERIFICATION = sensible tests/checks or clear \
next steps implied by the submission.
2. One line exactly: TOTAL: <sum>/4 (sum is the sum of the four 0/1 scores, an integer 0–4).
3. Optional: up to two additional lines of overall actionable revision guidance (still no reference-patch leakage).

{_NO_FEEDBACK_RULES}"""

_SINGLE_CRITERION_BLOCK = f"""If the first line is NO, you must add exactly two lines after it (sparse feedback):
1. First line exactly: VIOLATED: <ONE of PROBLEM_FIT, PATCH_QUALITY, SCOPE, VERIFICATION> — pick the single most \
serious failure. If multiple fail, report only the single highest-priority one (priority order: PROBLEM_FIT, \
PATCH_QUALITY, SCOPE, VERIFICATION).
2. Second line: exactly one concise sentence of actionable feedback for that criterion only. \
Do not mention other criteria, scores, or issues. Do not use bullet lists.

{_NO_FEEDBACK_RULES}"""


def swe_judge_prompt_for_mode(mode: JudgeFeedbackMode, *, variant: SubmissionVariant = "chat") -> str:
    """Full judge template with ``{question}``, ``{answer}``, ``{response}`` placeholders."""
    intro = _swe_intro(variant)
    if mode == "freeform":
        suffix = _FREEFORM_BLOCK
    elif mode == "total_score":
        suffix = _TOTAL_SCORE_BLOCK
    elif mode == "single_criterion":
        suffix = _SINGLE_CRITERION_BLOCK
    else:
        raise ValueError(f"Unknown judge_feedback_mode: {mode!r}")
    return intro + "\n\n" + suffix


# Default prompt (backward compatible).
SWE_SUBMISSION_JUDGE_PROMPT = swe_judge_prompt_for_mode("freeform", variant="chat")
