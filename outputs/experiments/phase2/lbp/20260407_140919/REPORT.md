# phase2/lbp · 20260407_140919

**Benchmark:** LongBench-Pro · Phase 2 (SKILL.md vs chat baselines)

*2026-04-07 14:40 UTC*

## Config

```json
{
  "model": "openai/gpt-4.1-mini",
  "judge_model": "openai/gpt-4.1-mini",
  "num_examples": 5,
  "rollouts_per_example": 1,
  "max_concurrent": 2,
  "num_workers": "auto",
  "seed": 42,
  "language": "English",
  "dataset_start_index": 0,
  "token_length": "all",
  "difficulty": "all",
  "thinking": false,
  "include_env_tips": false,
  "prompt_in_context_file": false,
  "max_turns_chat": 8,
  "max_turns_rlm": 30,
  "max_judge_submissions": 8,
  "env_dir_path": "./environments",
  "api_key_var": "PRIME_API_KEY",
  "api_base_url": "https://api.pinference.ai/api/v1",
  "client_type": "openai_chat_completions",
  "judge_sampling_args": {
    "temperature": 0.0
  },
  "sampling_args": {},
  "verbose": false,
  "debug": true,
  "save_results": true,
  "max_retries": 0,
  "shuffle": false,
  "phase1_slice": true,
  "phase2_skill_max_chars": 6000,
  "rlm_sandbox_cpu_cores": null,
  "rlm_sandbox_memory_gb": null,
  "rlm_sandbox_disk_size_gb": null,
  "rlm_sandbox_timeout_minutes": null,
  "rlm_code_execution_timeout": null,
  "rlm_sub_llm_max_turns": null
}
```

## Results

| Cell | Env | Phase 2 arm | Judge YES | Reward | Err | Task metric | @1 | @2 | @4 | @8 | Mean tok (success) | Median tok (success) | n succ | n | Wall (s) | Roll (s) | Tokens |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `chat__single_criterion__chat_no_file` | `longbenchpro` | `chat_no_file` | 0.0000 | 0.0000 | 0.0000 | 0.0500 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | — | — | 0 | 5 | 222.8 | 425.0 | 248,736 |
| `chat__single_criterion__chat_system_reinject` | `longbenchpro` | `chat_system_reinject` | 0.0000 | 0.0000 | 0.0000 | 0.0500 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | — | — | 0 | 5 | 149.6 | 280.6 | 248,271 |
| `chat__total_score__chat_no_file` | `longbenchpro` | `chat_no_file` | 0.0000 | 0.0000 | 0.0000 | 0.0500 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | — | — | 0 | 5 | 186.3 | 334.3 | 250,836 |
| `chat__total_score__chat_system_reinject` | `longbenchpro` | `chat_system_reinject` | 0.2000 | 0.2000 | 0.0000 | 0.2000 | 0.0000 | 0.0000 | 0.0000 | 0.2000 | 226,362 | 226,362 | 1 | 5 | 128.3 | 250.4 | 243,598 |
| `rlm__single_criterion__rlm_skill_file` | `longbenchpro-rlm` | `rlm_skill_file` | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | — | — | 0 | 5 | 217.8 | 398.2 | 15,507 |
| `rlm__total_score__rlm_skill_file` | `longbenchpro-rlm` | `rlm_skill_file` | 0.0000 | 0.0000 | 0.0000 | 0.0800 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | — | — | 0 | 5 | 937.9 | 1336.2 | 51,563 |

**Success@K** is the fraction of rollouts where the judge accepted (`judge_reward` ≥ 0.5) and round count ≤ K. Chat harness uses `num_turns` (assistant generations); RLM uses `root_llm_turns` (root REPL calls). **Mean tok (success)** / **Median tok (success)** aggregate total tokens (input + output) over judge-success rollouts when per-rollout `token_usage` is present (newer runs only; older `summary.json` files may leave these blank).
