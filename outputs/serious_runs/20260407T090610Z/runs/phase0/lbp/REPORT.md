# phase0 · lbp

**Benchmark:** phase0

*2026-04-10 13:04 UTC*

## Config

```json
{
  "model": "z-ai/glm-4.7",
  "judge_model": "z-ai/glm-4.7-flash",
  "num_examples": 15,
  "rollouts_per_example": 2,
  "max_concurrent": 16,
  "num_workers": "auto",
  "seed": 42,
  "language": "English",
  "dataset_start_index": 0,
  "token_length": "all",
  "difficulty": "all",
  "thinking": false,
  "include_env_tips": false,
  "prompt_in_context_file": false,
  "max_turns_chat": 32,
  "max_turns_rlm": 64,
  "max_judge_submissions": 16,
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
| `chat__single_criterion` | `longbenchpro` | 0.8667 | 0.8667 | 0.0000 | 0.6525 | 0.4667 | 0.7333 | 0.7667 | 0.8667 | 117,777 | 66,920 | 26 | 30 | 12457.3 | 58194.6 | 495,834 |
| `chat__total_score` | `longbenchpro` | 0.9667 | 0.9667 | 0.0000 | 0.6396 | 0.6333 | 0.7333 | 0.8667 | 0.9000 | 129,190 | 42,803 | 29 | 30 | 11990.3 | 57899.8 | 149,192 |
| `rlm__single_criterion` | `longbenchpro-rlm` | 0.7000 | 0.7000 | 0.0000 | 0.5351 | 0.0333 | 0.0333 | 0.1333 | 0.3000 | 74,244 | 25,835 | 21 | 30 | 2924.3 | 12650.2 | 106,936 |
| `rlm__total_score` | `longbenchpro-rlm` | 0.6667 | 0.6667 | 0.0000 | 0.4368 | 0.0000 | 0.0000 | 0.1000 | 0.3667 | 77,656 | 25,814 | 20 | 30 | 872.1 | 8700.0 | 119,868 |

**Success@K** is the fraction of rollouts where the judge accepted (`judge_reward` ≥ 0.5) and round count ≤ K. Chat harness uses `num_turns` (assistant generations); RLM uses `root_llm_turns` (root REPL calls). **Mean tok (success)** / **Median tok (success)** aggregate total tokens (input + output) over judge-success rollouts when per-rollout `token_usage` is present (newer runs only; older `summary.json` files may leave these blank).
