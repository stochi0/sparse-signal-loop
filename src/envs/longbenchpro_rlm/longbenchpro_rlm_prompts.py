"""LLM judge prompts for the LongBench-Pro environment (``longbenchpro-rlm``)."""

from __future__ import annotations

from typing import Literal

JudgeFeedbackMode = Literal["total_score", "single_criterion"]

_LBP_INTRO = """Given a ground truth answer and a model response, decide if the response is correct \
with respect to the question and the reference answer (allowing paraphrase and equivalent formatting when appropriate).

Question:
```
{question}
```

Ground truth answer:
```
{answer}
```

Model response:
```
{response}
```

Reply with exactly one word on the first line: YES if the response is correct, otherwise NO."""

_NO_FEEDBACK_RULES = """Strict rules for feedback after NO (all modes):
- Do NOT state, quote, hint at, or correct toward any specific value, name, date, number, span, or entity that \
appears in the ground truth but not in the model's response (no "should be … instead of …" when the replacement \
comes from the reference).
- Do NOT paste or paraphrase lines from the ground truth answer.
- DO give process guidance only where applicable: which part of the model's answer to re-check, format issues \
([Answer] / [答案], line order, missing items), or where in the long context to look again (section names, chronology), \
without disclosing what the passage says the answer is."""

_TOTAL_SCORE_BLOCK = f"""If the first line is NO, you must add the following lines after it (dense feedback):
1. Four lines, one per criterion, each exactly in this form (score must be 0 or 1 only):
   FORMAT: <0 or 1> — <one short note; no ground-truth leakage>
   COMPLETENESS: <0 or 1> — <one short note>
   GROUNDING: <0 or 1> — <one short note>
   RELEVANCE: <0 or 1> — <one short note>
2. One line exactly: TOTAL: <sum>/4 (sum is the sum of the four 0/1 scores, an integer 0–4).
3. Optional: up to two additional lines of overall actionable revision guidance (still no ground-truth leakage).

{_NO_FEEDBACK_RULES}"""

_SINGLE_CRITERION_BLOCK = f"""If the first line is NO, you must add exactly two lines after it (sparse feedback):
1. First line exactly: VIOLATED: <ONE of FORMAT, COMPLETENESS, GROUNDING, RELEVANCE> — pick the single most \
serious failure. If multiple fail, report only the single highest-priority one (priority order: GROUNDING, \
COMPLETENESS, RELEVANCE, FORMAT).
2. Second line: exactly one concise sentence of actionable feedback for that criterion only. \
Do not mention other criteria, scores, or issues. Do not use bullet lists.

{_NO_FEEDBACK_RULES}"""


def lbp_judge_prompt_for_mode(mode: JudgeFeedbackMode) -> str:
    """Return the full judge template (with ``{question}``, ``{answer}``, ``{response}`` placeholders)."""
    if mode == "total_score":
        suffix = _TOTAL_SCORE_BLOCK
    elif mode == "single_criterion":
        suffix = _SINGLE_CRITERION_BLOCK
    else:
        raise ValueError(f"Unknown judge_feedback_mode: {mode!r}")
    return _LBP_INTRO + "\n\n" + suffix


LBP_JUDGE_PROMPT = lbp_judge_prompt_for_mode("total_score")
