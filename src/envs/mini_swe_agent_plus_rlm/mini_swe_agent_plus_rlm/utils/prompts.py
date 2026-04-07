from __future__ import annotations

import re
from typing import Literal

from jinja2 import StrictUndefined, Template


def render_template(template: str, **kwargs) -> str:
    return Template(template, undefined=StrictUndefined).render(**kwargs)


REPL_PROMPT_TEMPLATE = """<pr_description>

Consider the following PR description:

{problem_statement}

</pr_description>

<instructions>

# Task Instructions (REPL)

You are operating in a REPL-backed coding environment. Use the `{repl_tool_name}` tool to run code
iteratively. The REPL preserves state across calls.

## Important Boundaries

- MODIFY: Regular source code files
- DO NOT MODIFY: Tests, configuration files (pyproject.toml, setup.cfg, etc.)

## Workspace vs. chat

The PR description is only in the messages above. Source code lives under `/testbed` (the REPL working tree)—inspect and edit files there. The `.messages` file in the REPL, if you open it, is JSONL for this **conversation** (`role`, `content`, …); it is not the repo and not a shortcut for reading project files.

## Recommended Workflow

1. Inspect the repo with `execute_bash` (via the allowed path)
2. Identify the bug or missing behavior
3. Apply edits with `edit_via_str_replace`
4. Validate behavior with targeted commands

## Submission

When you have a candidate fix, set:

```python
answer["content"] = "brief summary of what you changed"
answer["ready"] = True
```

If judge feedback in the REPL output says the submission was rejected, keep working and submit again the same way. \
 Leave enough root-model turns for explore + submit + possible revision after a NO.

</instructions>"""

ACTION_OBSERVATION_TEMPLATE = """<returncode>{{exit_code}}</returncode>
{% if output | length < 10000 -%}
<output>
{{ output -}}
</output>
{%- else -%}
<warning>
The output of your last command was too long.
Please try a different command that produces less output.
If you're looking at a file you can try use head, tail or sed to view a smaller number of lines selectively.
If you're using grep or find and it produced too much output, you can use a more selective search pattern.
If you really need to see something from the full command's output, you can redirect output to a file and then search in that file.
</warning>
{%- set elided_chars = output | length - 10000 -%}
<output_head>
{{ output[:5000] }}
</output_head>
<elided_chars>
{{ elided_chars }} characters elided
</elided_chars>
<output_tail>
{{ output[-5000:] }}
</output_tail>
{%- endif -%}"""

# Phase 1 — working memory scaffolding (kept in sync with mini_swe_agent_plus ``utils/prompts``)
Phase1MemoryMode = Literal["off", "chat", "repl_files"]

PHASE1_MSWE_DEFAULT_ONLY_REPOS: tuple[str, ...] = ("django/django",)

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
Store all of the above only in your assistant messages (plain text before or after your single tool call in each turn).
The chat transcript is your only durable notebook—there is no separate persistent note file for this purpose.
Compress or rewrite earlier notes when they grow too long.
</phase1_memory_location_chat>"""

_PHASE1_REPL_FILES_WHERE = """<phase1_memory_location_repl_files>
Persist the checklist, hypothesis log, and “what failed last time” lines in the sandbox as plain text under ``/testbed``
(e.g. ``/testbed/working_notes.md``). Read them back at the start of substantive work after tool results; update them
after discoveries or rejections. You may briefly summarize in chat, but the canonical copy must live in those files.
</phase1_memory_location_repl_files>"""

_PHASE1_RLM_CHAT_ABLATION = """<phase1_memory_location_rlm_chat_ablation>
Use the same checklist, hypothesis, and failure log as above, but keep them only in your root assistant messages
(between REPL tool calls). Do not rely on note files in the sandbox for this ablation—even though the REPL exists,
treat chat as the sole external memory for Phase 1 notes.
</phase1_memory_location_rlm_chat_ablation>"""


def phase1_working_memory_suffix(
    mode: Phase1MemoryMode,
    *,
    rlm: bool,
) -> str:
    """Append to the first user message body. ``repl_files`` requires ``rlm=True``."""
    if mode == "off":
        return ""
    blocks = [_PHASE1_CORE]
    if mode == "chat":
        blocks.append(_PHASE1_RLM_CHAT_ABLATION if rlm else _PHASE1_CHAT_WHERE)
    elif mode == "repl_files":
        if not rlm:
            raise ValueError("phase1_working_memory='repl_files' is only valid for mini_swe_agent_plus_rlm.")
        blocks.append(_PHASE1_REPL_FILES_WHERE)
    else:
        raise ValueError(f"Unknown phase1_working_memory mode: {mode!r}")
    return "\n\n" + "\n\n".join(blocks)


# =============================================================================
# Phase 2 — self-improving skill harness (prompting only)
# =============================================================================

Phase2SkillMode = Literal["off", "rlm_skill_file", "chat_no_file", "chat_system_reinject"]

_PHASE2_CORE = """<phase2_skill_harness>
Phase 2 — learned *procedure* only (no task spoilers):

You may record **how** you work: how you interpret judge feedback, self-checks before submit, and habits that prevent wasted tool calls.
Do **not** store final answers, unique gold spans, or long extracts presented as reference text.
</phase2_skill_harness>"""

_PHASE2_RLM_SKILL_FILE = """<phase2_skill_file>
The REPL workspace includes ``SKILL.md`` (seed template). Only the root model should edit it; it is **not** shown to the automatic judge (the judge grades submitted answers only).

After each ``NO`` from the judge, update ``SKILL.md`` with durable process lessons (still no spoilers; no pasted ground truth).

Soft size limit: about {max_chars} characters—compress older notes when needed.
</phase2_skill_file>"""

_PHASE2_CHAT_NO_FILE = """<phase2_chat_no_skill_file>
There is **no** separate skill file—only this chat and the judge feedback after each rejected submission. Improve by revising your changes; transient scratch in assistant messages is allowed but nothing else persists.
</phase2_chat_no_skill_file>"""

_PHASE2_CHAT_SYSTEM_REINJECT = """<phase2_chat_system_reinject>
**Weak memory baseline (no file):** If you wrap reusable *process* notes in exactly one pair of tags below in an assistant message, the environment may reinject **only** that inner text at the start of your next turn as an extra system message (not shown to the judge).

<phase2_skill>
...process notes only; no pasted reference or gold answers...
</phase2_skill>

Content outside these tags is not reinjected. Keep the inner text under ~{max_chars} characters.
</phase2_chat_system_reinject>"""


def build_phase2_skill_md_template(*, max_chars: int) -> str:
    """Seed text for ``SKILL.md`` when ``phase2_skill_mode='rlm_skill_file'``."""
    return f"""# Episode skill (process only)

Edit this file across REPL turns. Store **only** reusable *process* guidance, for example:
- How you read judge feedback and decide what to try next.
- A short self-check before each submission.

Do **not** paste ground-truth answers or long gold quotations. Do not duplicate your final submission text here.

Target length: stay under ~{max_chars} characters.

(Seed text—replace freely.)
"""


def phase2_skill_suffix(
    mode: Phase2SkillMode,
    *,
    rlm: bool,
    max_chars: int,
) -> str:
    """Append to the task query (after Phase 1 suffix when both are enabled)."""
    if mode == "off":
        return ""
    blocks = [_PHASE2_CORE]
    if mode == "rlm_skill_file":
        if not rlm:
            raise ValueError("phase2_skill_mode='rlm_skill_file' is only valid for RLM harness envs.")
        blocks.append(_PHASE2_RLM_SKILL_FILE.format(max_chars=max_chars))
        return "\n\n" + "\n\n".join(blocks)
    if mode == "chat_no_file":
        if rlm:
            raise ValueError("phase2_skill_mode='chat_no_file' is for the chat harness only.")
        blocks.append(_PHASE2_CHAT_NO_FILE)
        return "\n\n" + "\n\n".join(blocks)
    if mode == "chat_system_reinject":
        if rlm:
            raise ValueError("phase2_skill_mode='chat_system_reinject' is for the chat harness only.")
        blocks.append(_PHASE2_CHAT_SYSTEM_REINJECT.format(max_chars=max_chars))
        return "\n\n" + "\n\n".join(blocks)
    raise ValueError(f"Unknown phase2_skill_mode: {mode!r}")


def extract_phase2_skill_block(text: str) -> str | None:
    """Return inner text of the last ``<phase2_skill>...</phase2_skill>`` block, if any."""
    if not text:
        return None
    matches = list(
        re.finditer(r"<phase2_skill>\s*(.*?)\s*</phase2_skill>", text, flags=re.DOTALL | re.IGNORECASE)
    )
    if not matches:
        return None
    inner = matches[-1].group(1).strip()
    return inner or None
