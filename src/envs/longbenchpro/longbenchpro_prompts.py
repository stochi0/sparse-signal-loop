"""LLM judge prompts for the LongBench-Pro environment (``longbenchpro``)."""

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

# =============================================================================
# Phase 1 — working-memory scaffolding (prompting only; compare chat vs REPL files in RLM)
# =============================================================================

Phase1MemoryMode = Literal["off", "chat", "repl_files"]

PHASE1_LBP_DEFAULT_SECONDARY_TASK = "T6.1 Large-Scale Document Clustering"
PHASE1_LBP_DEFAULT_TOKEN_LENGTH = "32k"

_PHASE1_CORE = """<phase1_working_memory>
Phase 1 — structured working memory (prompting only; no RL):

Throughout the episode, maintain lightweight structure so you do not repeat dead ends:
- A short checklist (about five bullets max) of what remains to verify or answer.
- A one-to-two-line hypothesis log: your current best guess and why.
- After each failed attempt, wrong answer, or judge/tool rejection, append one line to
  “what failed last time” (describe the symptom or feedback only; do not invent ground truth).

Update these artifacts as you learn. They are for your own coordination, not part of the final answer format
unless the task explicitly asks for them.
</phase1_working_memory>"""

_PHASE1_CHAT_WHERE = """<phase1_memory_location_chat>
Store all of the above only in your assistant messages (plain text, e.g. at the start or end of each turn).
The chat transcript is your only durable notebook—there is no separate persistent note file for this purpose.
Compress or rewrite earlier notes when they grow too long.
</phase1_memory_location_chat>"""

_PHASE1_REPL_FILES_WHERE = """<phase1_memory_location_repl_files>
Persist the checklist, hypothesis log, and “what failed last time” lines in the REPL workspace as plain text
(e.g. ``working_notes.md`` in the current directory or ``/tmp/phase1_notes.txt``). At the start of substantive
REPL work each turn, read them back; after discoveries or rejections, update them. You may briefly summarize
in chat, but the canonical copy must live in those files so it survives across REPL calls.
</phase1_memory_location_repl_files>"""

_PHASE1_RLM_CHAT_ABLATION = """<phase1_memory_location_rlm_chat_ablation>
Use the same checklist, hypothesis, and failure log as above, but keep them only in your root assistant messages
(between REPL tool calls). Do not rely on note files in the REPL for this ablation—even though the REPL exists,
treat chat as the sole external memory for Phase 1 notes.
</phase1_memory_location_rlm_chat_ablation>"""


def phase1_working_memory_suffix(
    mode: Phase1MemoryMode,
    *,
    rlm: bool,
) -> str:
    """Append to the task query stem. ``repl_files`` requires ``rlm=True``."""
    if mode == "off":
        return ""
    blocks = [_PHASE1_CORE]
    if mode == "chat":
        blocks.append(_PHASE1_RLM_CHAT_ABLATION if rlm else _PHASE1_CHAT_WHERE)
    elif mode == "repl_files":
        if not rlm:
            raise ValueError("phase1_working_memory='repl_files' is only valid for RLM environments.")
        blocks.append(_PHASE1_REPL_FILES_WHERE)
    else:
        raise ValueError(f"Unknown phase1_working_memory mode: {mode!r}")
    return "\n\n" + "\n\n".join(blocks)


def resolve_phase1_lbp_filters(
    *,
    phase1_slice: bool,
    secondary_task: str | None,
    token_length: str,
) -> tuple[str | None, str]:
    """When ``phase1_slice``, default to T6.1 @ 32k if filters are still broad."""
    st = secondary_task
    tl = token_length
    if not phase1_slice:
        return st, tl
    if st is None:
        st = PHASE1_LBP_DEFAULT_SECONDARY_TASK
    if tl == "all":
        tl = PHASE1_LBP_DEFAULT_TOKEN_LENGTH
    return st, tl
