from __future__ import annotations

from typing import Literal

from jinja2 import StrictUndefined, Template


def render_template(template: str, **kwargs) -> str:
    return Template(template, undefined=StrictUndefined).render(**kwargs)


PROMPT_TEMPLATE = """<pr_description>

Consider the following PR description:

{problem_statement}

</pr_description>

<instructions>

# Task Instructions

## Overview

You're a software engineer interacting continuously with a computer by submitting tool calls.

You'll be helping implement necessary changes to meet requirements in the PR description.

Your task is specifically to make changes to non-test files in the current directory in order to fix the issue described in the PR description in a way that is general and consistent with the codebase.

IMPORTANT: This is an interactive process where you will think and issue ONE tool call, see its result, then think and issue your next tool call.

For each response provide exactly ONE tool call to execute.

## Important Boundaries

- MODIFY: Regular source code files

- DO NOT MODIFY: Tests, configuration files (pyproject.toml, setup.cfg, etc.)

## Recommended Workflow

1. Analyze the codebase by finding and reading relevant files

2. Create a script to reproduce the issue

3. Edit the source code to resolve the issue

4. Verify your fix works by running your script again

5. Test edge cases to ensure your fix is robust

## Command Execution Rules

You are operating in an environment where

1. You issue a single tool call with the tool name and arguments

2. The system executes that tool call in a subshell

3. You see the result

4. You issue your next tool call

Each response should include a single tool call with the tool name and arguments.

**CRITICAL REQUIREMENTS:**

- Your response MUST include EXACTLY ONE tool call

- If you include zero or multiple tool calls, or no tool call at all, YOUR RESPONSE WILL FAIL

- Do NOT try to run multiple independent tool calls in one response

- Directory or environment variable changes are not persistent. Every action is executed in a new subshell.

- However, you can prefix any action with `MY_ENV_VAR=MY_VALUE cd /path/to/working/dir && ...` or write/load environment variables from files

If you need to run multiple commands, either:

1. Combine them in one block using && or || using your tool call


command1 && command2 || echo "Error occurred"


2. Wait for the first tool call to complete, see its output, then issue the next tool call in your following response.

## Environment Details

- You have a full Linux shell environment

- Always use non-interactive flags (-y, -f) for commands

- Avoid interactive tools like vi, nano, or any that require user input

- If a command isn't available, you can install it

## Useful Command Examples

### Create a new file:


cat <<'EOF' > newfile.py

import numpy as np

hello = "world"

print(hello)

EOF


### View file content:


# View specific lines with numbers

nl -ba filename.py | sed -n '10,20p'


### Any other command you want to run using your tool call


anything


## Submission

When you have a candidate fix (or must stop), submit it for checking by issuing exactly this command in one tool call:


echo MINI_SWE_AGENT_FINAL_OUTPUT


If the tool output includes judge feedback that your submission was rejected, read it, make further edits with \
execute_bash or edit_via_str_replace, and submit again the same way. Reserve enough turns for at least one submit \
plus possible revision cycles. When feedback indicates acceptance (or the episode ends for other reasons), stop.

</instructions>"""

SYSTEM_PROMPT = """You are a helpful assistant that can interact multiple times with tools to solve programming tasks.

Your response must contain exactly ONE tool call with the tool name and arguments.

Failure to follow these rules will cause your response to be rejected."""

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

FORMAT_ERROR_TEMPLATE = """Please always provide EXACTLY ONE tool call, found {{actions|length}} tool calls.

If you have completed your assignment, follow the submission instructions in the first user message."""

# Phase 1 — working memory scaffolding (prompting only; ``repl_files`` only for RLM package)
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
