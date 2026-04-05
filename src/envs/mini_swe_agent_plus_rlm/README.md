# mini-swe-agent-plus-rlm

<a href="https://github.com/PrimeIntellect-ai/research-environments/tree/main/environments/mini_swe_agent_plus_rlm">
<img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white" alt="Source Code">
</a>

`mini-swe-agent-plus-rlm` solves SWE-style tasks in prime sandboxes using a persistent code REPL and optional sub-LLM tool use.

Upstream workflow reference: [mini-swe-agent-plus](https://github.com/Kwai-Klear/mini-swe-agent-plus).

Supported harnesses and datasets:

- all R2E-Gym datasets, incl.
  - [R2E-Gym-Subset](https://huggingface.co/datasets/R2E-Gym/R2E-Gym-Subset)
  - [SWE-Bench-Lite](https://huggingface.co/datasets/R2E-Gym/SWE-Bench-Lite)
  - [SWE-Bench-Verified](https://huggingface.co/datasets/R2E-Gym/SWE-Bench-Verified)
- all SWE-Bench datasets, e.g.
  - [SWE-bench Verified](https://huggingface.co/datasets/SWE-bench/SWE-bench_Verified)

### Overview

- **Environment ID**: `mini-swe-agent-plus-rlm`
- **Short description**: Sandbox SWE tasks with a code REPL and optional sub-LLM tools
- **Tags**: coding, multi-turn, sandbox, repl

### Datasets

- **Primary dataset(s)**: R2E-Gym/R2E-Gym-Subset, SWE-bench/SWE-bench_Verified, PrimeIntellect/SWE-Bench-Verified-Quick
- **Source links**: https://huggingface.co/datasets/R2E-Gym/R2E-Gym-Subset

### Task

- **Type**: multi-turn, tool use
- **Rubric overview**: Reward based on executing repo test-suite
- **Protected files**: Modifying test/config files yields a reward of 0 and tests are skipped.

### Iterative LLM judge
Set `iterative_judge` to **true** to run an LLM judge when the model submits from the REPL (`answer["ready"] = True` or bash `RLM_READY` when required by the harness). The judge sees the declared final answer plus `git diff` and the dataset gold `patch` when present. If the judge says **NO**, feedback is appended to the REPL tool result, `final_answer` is cleared, and the root model can continue until `max_judge_submissions` wrong attempts. **Primary reward remains** test-based `solved` (weight 1.0); `judge_reward` is weight 0.0 for diagnostics. Default is **false** (no judge API).

### Quickstart

Run an evaluation with default settings:

```bash
prime eval run mini-swe-agent-plus-rlm
```

To run SWE-Bench-Verified

```bash
prime eval run mini-swe-agent-plus-rlm -n -1 -r 1 -a '{"dataset_name": "SWE-bench/SWE-bench_Verified", "allow_git": true}'
```

To run a quicker version of SWE-Bench-Verified (downsampled to 468 examples)

```bash
prime eval run mini-swe-agent-plus-rlm -n -1 -r 1 -a '{"dataset_name": "PrimeIntellect/SWE-Bench-Verified-Quick", "allow_git": true}'
```

Notes:

- Use `-a` / `--env-args` to pass environment-specific configuration as a JSON object.

### Environment Arguments

| Arg | Type | Default | Description |
| --- | ---- | ------- | ----------- |
| `dataset_name` | str | `"R2E-Gym/R2E-Gym-Subset"` | Selects dataset |
| `max_turns` | int | `200` | Limits max number of agent turns |
| `sandbox_timeout_minutes` | int | `600` | Total sandbox container lifetime in minutes (10h). Must fit rollout + tests + 5 min margin. |
| `code_execution_timeout` | int | `120` | Per-action timeout in seconds for REPL executions, execute_bash, and edit_via_str_replace |
| `test_timeout` | int | `900` | Timeout for running tests after the rollout (seconds) |
| `cpu_cores` | int | `4` | Number of CPU cores for the sandbox |
| `memory_gb` | int | `4` | Amount of memory (GB) for the sandbox |
| `disk_size_gb` | int | `2` | Disk size (GB) for the sandbox |
| `sandbox_labels` | list[str] | `[]` | Additional sandbox labels (default `mini-swe-agent-plus-rlm` is always applied) |
| `max_execution_timeouts` | int | `5` | Abort rollout after this many command timeouts |
| `max_startup_wait_seconds` | int | `None` | Override infrastructure command timeout (default: `max(120, code_execution_timeout)`) |
| `allow_git` | bool | `False` | Allow git commands in execute_bash tool |
| `filter_repos` | list[str] | `None` | Exclude these repos from dataset, e.g. `scikit-learn/scikit-learn` |
| `tools_on_root` | bool | `False` | Make execute_bash/edit_via_str_replace available as standard tools (direct tool calling alongside the REPL) |
| `tools_in_repl` | bool | `False` | Make execute_bash/edit_via_str_replace available inside the REPL (callable as functions via HTTP proxy) |
| `tools_on_sub` | bool | `True` | Make execute_bash/edit_via_str_replace available to sub-LLMs |
| `include_sub_llm_in_trajectory` | bool | `False` | Include sub-LLM turns in trajectory |
| `sub_model` | str | `None` | Optional model override for sub-LLMs |
| `repl_language` | str | `"python"` | REPL language (python or bash) |
| `rlm_metric_weights` | dict[str, float] | `None` | Override weights for harness monitor metrics as training reward signals. See below. |
| `use_dataset_cache` | bool | `False` | Use HuggingFace dataset caching instead of keeping data in memory |
| `custom_instructions` | str | `""` | Extra instructions appended to each prompt in a `<custom_instructions>` block. Empty string adds nothing. |
| `iterative_judge` | bool | `False` | LLM judge on each REPL final submission when true |
| `max_judge_submissions` | int | `8` | Max incorrect submissions before the rollout is forced to end |
| `judge_model` | str | `openai/gpt-4.1-mini` | Judge model id (Prime Inference–style) |
| `judge_api_key_var` | str | `PRIME_API_KEY` | Env var for judge API key |
| `judge_base_url` | str | `None` | OpenAI-compatible base URL (default Prime Inference) |
| `judge_sampling_args` | dict | `None` | Optional sampling args for the judge chat call |
| `judge_feedback_mode` | str | `total_score` | When `iterative_judge` is true: `total_score` or `single_criterion` (criteria `PROBLEM_FIT`, `PATCH_QUALITY`, `SCOPE`, `VERIFICATION`). |

#### Timeout design

There are only three primary timeout knobs. Everything else is derived:

- **`sandbox_timeout_minutes`** -- Total sandbox lifetime. The platform kills the container after this.
- **`code_execution_timeout`** -- Per-action budget. Applied uniformly to REPL code, bash commands, and edits. The sub-LLM HTTP timeout is auto-derived as `code_execution_timeout - 5`.
- **`test_timeout`** -- Post-rollout test budget. Independent because tests have different runtime characteristics.

Derived (not user-facing):

- `rollout_timeout_seconds = sandbox_timeout_minutes * 60 - test_timeout - 300`
- `sandbox_command_timeout = code_execution_timeout`
- `sub_llm_timeout = code_execution_timeout - 5` (set by the recursive harness base class)

### Monitor metric weights (`rlm_metric_weights`)

By default, harness monitor metrics are tracked with weight 0 (monitor-only). Use `rlm_metric_weights` to assign nonzero weights so they contribute to the training reward.

Metrics are **min-max normalized within each group** of rollouts before the weight is applied, so the reward contribution is always in [0, 1] regardless of the metric's natural scale. Best-in-group gets 1.0, worst gets 0.0; when all rollouts have the same value, all get 0.0 (no signal). Use a positive weight to reward higher values (e.g., encourage larger batch sizes) or a negative weight to penalize them (e.g., discourage token usage).

Allowed keys:

| Key | Description |
| --- | ----------- |
| `sub_llm_call_count` | Total number of individual sub-LLM calls |
| `sub_llm_total_turns` | Total turns across all sub-LLM calls |
| `sub_llm_prompt_tokens` | Prompt tokens consumed by sub-LLMs |
| `sub_llm_completion_tokens` | Completion tokens consumed by sub-LLMs |
| `sub_llm_total_tool_calls` | Total tool calls made by sub-LLMs |
| `sub_llm_batch_count` | Number of `llm_batch` invocations |
| `sub_llm_mean_batch_size` | Average batch size across `llm_batch` calls |

Example (penalize excessive sub-LLM calls, reward batching):

```bash
prime eval run mini-swe-agent-plus-rlm -a '{"rlm_metric_weights": {"sub_llm_call_count": -0.01, "sub_llm_batch_count": 0.05}}'
```

The raw (unnormalized) metrics are still tracked as monitor-only metrics by the environment.

### Metrics

| Metric | Meaning |
| ------ | ------- |
| `solved` | If SWE task instance was correctly solved |
| `command_timeout_count` | Number of commands that timed out during rollout |
| `rollout_duration_seconds` | Wall-clock duration of the rollout |
| `sandbox_oom` | Sandbox was killed due to out-of-memory |
| `sandbox_timeout` | Sandbox timed out |
| `sandbox_image_pull_error` | Failed to pull sandbox docker image |

### Changelog

- 0.1.6: add `custom_instructions` parameter; replace `tool_target` enum with three independent booleans (`tools_on_root`, `tools_in_repl`, `tools_on_sub`); remove redundant tool instructions from prompt (handled by harness scaffolding)
- 0.1.5: simplify timeouts to 3 primary knobs (`sandbox_timeout_minutes`, `code_execution_timeout`, `test_timeout`); remove redundant `sandbox_command_timeout`, `rollout_timeout_seconds`, `total_timeout_minutes` (now derived); rename `max_command_timeouts` → `max_execution_timeouts`; add `max_startup_wait_seconds` power-user override. **Default changes**: sandbox lifetime 360 → 600 min, per-command timeout 90 → 120s (now unified with `code_execution_timeout`), derived rollout timeout 5400 → 34800s
- 0.1.4: add `use_dataset_cache` to opt into HuggingFace disk caching instead of in-memory datasets
- 0.1.3: align arg names with simplified recursive harness (`max_iterations` → `max_turns`, remove `execution_backend`, `sandbox_start_command`, `sandbox_client_max_workers`); `code_execution_timeout` now defaults to `120` instead of falling back to `sandbox_command_timeout`
- 0.1.2: sandbox labels no longer force in the default label
- 0.1.1: add `rlm_metric_weights` parameter with within-group min-max normalized harness metrics as training reward signals
- 0.1.0: initial release with recursive REPL harness
