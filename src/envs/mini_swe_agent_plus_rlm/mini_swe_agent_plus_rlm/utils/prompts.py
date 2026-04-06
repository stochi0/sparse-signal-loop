from __future__ import annotations

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
