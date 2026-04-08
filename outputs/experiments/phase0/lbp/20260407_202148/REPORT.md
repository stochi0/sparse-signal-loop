# phase0/lbp · 20260407_202148

**Benchmark:** LongBench-Pro (LBP)

*2026-04-08 01:29 UTC*

## Config

```json
{
  "model": "z-ai/glm-4.7-flash",
  "judge_model": "z-ai/glm-4.7-flash",
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
  "shuffle": false
}
```

## Results

| Cell | Env | Judge YES | Reward | Err | Task metric | @1 | @2 | @4 | @8 | Mean tok (success) | Median tok (success) | n succ | n | Wall (s) | Roll (s) | Tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `chat__single_criterion` | `longbenchpro` | 0.4000 | 0.4000 | 0.0000 | 0.6847 | 0.2000 | 0.2000 | 0.2000 | 0.4000 | 41,876 | 41,876 | 2 | 5 | 7395.8 | 10384.4 | 181,718 |
| `chat__total_score` | `longbenchpro` | 0.6000 | 0.6000 | 0.0000 | 0.5647 | 0.4000 | 0.6000 | 0.6000 | 0.6000 | 22,332 | 12,858 | 3 | 5 | 8285.1 | 11796.4 | 214,135 |
| `rlm__single_criterion` | `longbenchpro-rlm` | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | — | — | 0 | 5 | 1192.7 | 2222.3 | 149,167 |
| `rlm__total_score` | `longbenchpro-rlm` | 0.2000 | 0.2000 | 0.6000 | 0.1333 | 0.0000 | 0.0000 | 0.0000 | 0.2000 | 6,742 | 6,742 | 1 | 5 | 1545.8 | 3083.6 | 143,603 |

**Success@K** is the fraction of rollouts where the judge accepted (`judge_reward` ≥ 0.5) and round count ≤ K. Chat harness uses `num_turns` (assistant generations); RLM uses `root_llm_turns` (root REPL calls). **Mean tok (success)** / **Median tok (success)** aggregate total tokens (input + output) over judge-success rollouts when per-rollout `token_usage` is present (newer runs only; older `summary.json` files may leave these blank).
