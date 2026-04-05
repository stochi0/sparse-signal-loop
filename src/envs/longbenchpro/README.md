# longbenchpro

### Overview

- **Environment ID**: `longbenchpro`
- **Short description**: [LongBench-Pro](https://github.com/caskcsg/longcontext/tree/main/LongBench-Pro) in a normal chat setting (full context in the user message), with the same LLM judge and task metrics as `longbenchpro-rlm`.
- **Tags**: long-context, benchmark, judge, multi-turn (optional)

### How it differs from `longbenchpro-rlm`

| | `longbenchpro` | `longbenchpro-rlm` |
| --- | --- | --- |
| Context delivery | Inlined in the user prompt (or JSON block; see `prompt_in_context_file`) | Short user message + `context` in sandbox / structured file |
| Tooling | None | `RLMEnv` REPL, `llm_batch`, etc. |
| Iterative judge | After **every** assistant turn (`MultiTurnEnv`) | After each REPL **submit** (`final_answer`) |

Summarization tasks (T4.x) are excluded in both environments.

### Judge feedback modes (2×2 with `longbenchpro-rlm`)

Use `judge_feedback_mode` to cross dense vs sparse judge feedback with chat vs RLM (same judge model and dataset filters in all cells):

| | `total_score` | `single_criterion` |
| --- | --- | --- |
| Chat (`longbenchpro`) | `-a '{"judge_feedback_mode": "total_score", "iterative_judge": true, "max_turns": 8}'` | `-a '{"judge_feedback_mode": "single_criterion", ...}'` |
| RLM (`longbenchpro-rlm`) | `-a '{"judge_feedback_mode": "total_score", "max_judge_submissions": 8}'` | `-a '{"judge_feedback_mode": "single_criterion", ...}'` |

`freeform` (default) matches the original unstructured feedback after `NO`. Align `max_turns` with `max_judge_submissions` so graded revision attempts are comparable; total tokens still differ because of REPL exploration.

### Paired eval (same item + same judge feedback mode)

Use **identical** `-a` / `--env-args` JSON for chat vs RLM except where the harness differs (`max_turns` chat vs `max_judge_submissions` RLM). Set `shuffle: false` and the same `dataset_start_index` (skip the first N rows after filters and transform; same semantics as `mini-swe-agent-plus`) so both runs see the same problem. Use the same `judge_feedback_mode` and `judge_model`.

Example (`vf-eval` from repo root after `uv pip install -e ./environments/longbenchpro -e ./environments/longbenchpro_rlm`). Replace `YOUR_MODEL`; increase `dataset_start_index` to move through the filtered dataset.

```bash
# Same logical row: first English example after T4 exclusion (`dataset_start_index` 0).
ARGS=$(printf '%s' "{\"shuffle\":false,\"language\":\"English\",\"thinking\":false,\"include_env_tips\":false,\"prompt_in_context_file\":false,\"iterative_judge\":true,\"judge_feedback_mode\":\"total_score\",\"judge_model\":\"openai/gpt-4.1-mini\",\"dataset_start_index\":0,\"max_turns\":8}")
uv run vf-eval longbenchpro -m YOUR_MODEL -n 1 -r 1 -d -v -a "$ARGS"

ARGS_RLM=$(printf '%s' "{\"shuffle\":false,\"language\":\"English\",\"thinking\":false,\"include_env_tips\":false,\"prompt_in_context_file\":false,\"iterative_judge\":true,\"judge_feedback_mode\":\"total_score\",\"judge_model\":\"openai/gpt-4.1-mini\",\"dataset_start_index\":0,\"max_judge_submissions\":8}")
uv run vf-eval longbenchpro-rlm -m YOUR_MODEL -n 1 -r 1 -d -v -a "$ARGS_RLM"
```

`prime eval` (paths as in your setup):

```bash
ARGS=$(printf '%s' "{\"shuffle\":false,\"language\":\"English\",\"judge_feedback_mode\":\"single_criterion\",\"judge_model\":\"z-ai/glm-4.7\",\"dataset_start_index\":0,\"max_turns\":8}")
prime eval run longbenchpro --env-dir-path ./environments -m z-ai/glm-4.7 -n 1 -r 1 -d -v -a "$ARGS"

ARGS_RLM=$(printf '%s' "{\"shuffle\":false,\"language\":\"English\",\"judge_feedback_mode\":\"single_criterion\",\"judge_model\":\"z-ai/glm-4.7\",\"dataset_start_index\":0,\"max_judge_submissions\":8}")
prime eval run longbenchpro-rlm --env-dir-path ./environments -m z-ai/glm-4.7 -n 1 -r 1 -d -v -a "$ARGS_RLM"
```

Rollout `info` includes `dataset_example_id` (the HuggingFace row `id`) for logging. To target a specific `id`, load the dataset with the same filters in Python, find its index in the filtered table, and pass that as `dataset_start_index`.

### Dataset

- [caskcsg/LongBench-Pro](https://huggingface.co/datasets/caskcsg/LongBench-Pro)

Default language filter is **English** (~750 samples). Use `language: "Chinese"` or `"all"` to change.

### Quickstart

```bash
uv pip install -e ./environments/longbenchpro

# Single rollout (iterative judge on by default)
uv run vf-eval longbenchpro -m gpt-5-mini -n 1 -r1 -d -v

# Single-turn (judge only at end)
uv run vf-eval longbenchpro -m gpt-5-mini -n 5 -a '{"iterative_judge": false}'

# Match RLM-style JSON payload (still in chat, not on disk)
uv run vf-eval longbenchpro -m gpt-5-mini -n 3 -a '{"prompt_in_context_file": true}'
```

### Environment arguments

| Arg | Type | Default | Description |
| --- | ---- | ------- | ----------- |
| `split` | str | `"test"` | Dataset split |
| `shuffle` | bool | `False` | Shuffle dataset |
| `seed` | int \| None | `None` | Shuffle seed |
| `thinking` | bool | `False` | Use `question_thinking` vs `question_nonthinking` |
| `include_env_tips` | bool | `False` | Append non-RLM reading tips |
| `prompt_in_context_file` | bool | `False` | If true, user message is JSON `{"query","context"}`; if false, query + `## Long Context` section |
| `language` | str | `"English"` | `"English"`, `"Chinese"`, or `"all"` |
| `token_length` | str | `"all"` | Length bucket filter |
| `difficulty` | str | `"all"` | Difficulty filter |
| `primary_task` | str \| None | `None` | Primary task filter |
| `secondary_task` | str \| None | `None` | Secondary task filter |
| `dataset_start_index` | int | `0` | Skip first N rows after filters and transform (like `mini-swe-agent-plus`; pair chat/RLM with the same value) |
| `judge_model` | str | `"gpt-4.1-mini"` | Judge model (OpenAI-compatible) |
| `judge_api_key_var` | str | `"PRIME_API_KEY"` | API key env var |
| `judge_base_url` | str \| None | `None` | Default: Prime Inference |
| `judge_sampling_args` | dict \| None | `None` | Judge sampling kwargs |
| `judge_feedback_mode` | str | `"freeform"` | `"freeform"`, `"total_score"` (four 0/1 criteria + `TOTAL: x/4`), or `"single_criterion"` (one `VIOLATED:` line + one sentence) |
| `iterative_judge` | bool | `True` | Multi-turn feedback vs single-turn |
| `max_turns` | int | `8` | Max assistant messages when `iterative_judge` is true |

### Metrics

Same as `longbenchpro-rlm`: primary reward is `judge_reward` (weight 1.0); `task_metric_reward` and `contains_answer_reward` at weight 0 for analysis.

### Changelog

- 0.1.5: Removed `lbp_id` loader arg; rollout `info` uses `dataset_example_id` instead of `lbp_id`.
- 0.1.4: `dataset_start_index` (same semantics as `mini-swe-agent-plus` / `mini-swe-agent-plus-rlm`).
- 0.1.3: `lbp_id` to pin one dataset row; README paired-eval commands for chat vs RLM with the same item and `judge_feedback_mode`.
- 0.1.2: Prompt module scoped to this package only; mirror copy is `longbenchpro_rlm_prompts.py` in `longbenchpro-rlm`.
- 0.1.1: `judge_feedback_mode` (`freeform` / `total_score` / `single_criterion`); prompts in `longbenchpro_prompts.py`.
- 0.1.0: Initial non-RLM release (parity with `longbenchpro_rlm` dataset, judge, and metrics)
