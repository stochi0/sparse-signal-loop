# longbenchpro

### Overview

- **Environment ID**: `longbenchpro`
- **Short description**: [LongBench-Pro](https://github.com/caskcsg/longcontext/tree/main/LongBench-Pro) with full context in the user message, optional LLM judge, and benchmark task metrics.
- **Tags**: long-context, benchmark, judge, multi-turn (optional)

Summarization tasks (T4.x) are excluded.

### Judge feedback modes

`judge_feedback_mode` controls how the judge formats feedback after `NO`:

- `total_score` (default): four 0/1 criterion lines plus `TOTAL: x/4`.
- `single_criterion`: one `VIOLATED:` line plus one sentence.

For iterative judging, set `iterative_judge: true` and tune `max_turns` for enough room to revise after feedback.

### Dataset

- [caskcsg/LongBench-Pro](https://huggingface.co/datasets/caskcsg/LongBench-Pro)

Default language filter is **English** (~750 samples). Use `language: "Chinese"` or `"all"` to change.

Rollout `info` includes `dataset_example_id` (the HuggingFace row `id`) for logging.

### Quickstart

```bash
uv pip install -e ./environments/longbenchpro

# Single rollout (iterative judge on by default)
uv run vf-eval longbenchpro -m gpt-5-mini -n 1 -r1 -d -v

# Single-turn (judge only at end)
uv run vf-eval longbenchpro -m gpt-5-mini -n 5 -a '{"iterative_judge": false}'

# User message as JSON {"query","context"} instead of markdown long-context section
uv run vf-eval longbenchpro -m gpt-5-mini -n 3 -a '{"prompt_in_context_file": true}'
```

### Environment arguments

| Arg | Type | Default | Description |
| --- | ---- | ------- | ----------- |
| `split` | str | `"test"` | Dataset split |
| `shuffle` | bool | `False` | Shuffle dataset |
| `seed` | int \| None | `None` | Shuffle seed |
| `thinking` | bool | `False` | Use `question_thinking` vs `question_nonthinking` |
| `include_env_tips` | bool | `False` | Append optional reading-strategy tips |
| `prompt_in_context_file` | bool | `False` | If true, user message is JSON `{"query","context"}`; if false, query + `## Long Context` section |
| `language` | str | `"English"` | `"English"`, `"Chinese"`, or `"all"` |
| `token_length` | str | `"all"` | Length bucket filter |
| `difficulty` | str | `"all"` | Difficulty filter |
| `primary_task` | str \| None | `None` | Primary task filter |
| `secondary_task` | str \| None | `None` | Secondary task filter |
| `dataset_start_index` | int | `0` | Skip first N rows after filters and transform |
| `judge_model` | str | `"gpt-4.1-mini"` | Judge model (OpenAI-compatible) |
| `judge_api_key_var` | str | `"PRIME_API_KEY"` | API key env var |
| `judge_base_url` | str \| None | `None` | Default: Prime Inference |
| `judge_sampling_args` | dict \| None | `None` | Judge sampling kwargs |
| `judge_feedback_mode` | str | `"total_score"` | `total_score` or `single_criterion` |
| `iterative_judge` | bool | `True` | Multi-turn feedback vs single-turn |
| `max_turns` | int | `8` | Max assistant messages when `iterative_judge` is true |

### Metrics

Primary reward is `judge_reward` (weight 1.0); `task_metric_reward` and `contains_answer_reward` at weight 0 for analysis.

### Changelog

- 0.1.5: Removed `lbp_id` loader arg; rollout `info` uses `dataset_example_id` instead of `lbp_id`.
- 0.1.4: `dataset_start_index`.
- 0.1.3: `lbp_id` to pin one dataset row.
- 0.1.2: Prompt module scoped to this package (`longbenchpro_prompts.py`).
- 0.1.1: `judge_feedback_mode` (`total_score` / `single_criterion`).
- 0.1.0: Initial release.
