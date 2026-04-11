# phase2 · lbp

**Benchmark:** phase2

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
  "shuffle": false,
  "phase1_slice": true,
  "phase2_skill_max_chars": 16000,
  "rlm_sandbox_cpu_cores": 4,
  "rlm_sandbox_memory_gb": 16,
  "rlm_sandbox_disk_size_gb": 16,
  "rlm_sandbox_timeout_minutes": 120,
  "rlm_code_execution_timeout": 180,
  "rlm_sub_llm_max_turns": 128
}
```

## Results

| Cell | Env | Phase 2 arm | Judge YES | Reward | Err | Task metric | @1 | @2 | @4 | @8 | Mean tok (success) | Median tok (success) | n succ | n | Wall (s) | Roll (s) | Tokens |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `chat__single_criterion__chat_no_file` | `longbenchpro` | `chat_no_file` | 0.3000 | 0.3000 | 0.0000 | 0.4000 | 0.1000 | 0.1000 | 0.2000 | 0.3000 | 209,713 | 216,922 | 3 | 10 | 14507.1 | 73675.3 | 1,709,048 |
| `chat__single_criterion__chat_system_reinject` | `longbenchpro` | `chat_system_reinject` | 0.6000 | 0.6000 | 0.1000 | 0.6000 | 0.2000 | 0.3000 | 0.5000 | 0.5000 | 225,820 | 116,658 | 6 | 10 | 24950.2 | 75109.0 | 980,901 |
| `chat__total_score__chat_no_file` | `longbenchpro` | `chat_no_file` | 0.5000 | 0.5000 | 0.2000 | 0.5900 | 0.2000 | 0.2000 | 0.3000 | 0.4000 | 216,369 | 174,701 | 5 | 10 | 30173.5 | 129935.5 | 985,639 |
| `chat__total_score__chat_system_reinject` | `longbenchpro` | `chat_system_reinject` | 0.4000 | 0.4000 | 0.0000 | 0.4200 | 0.2000 | 0.2000 | 0.3000 | 0.3000 | 699,694 | 151,988 | 4 | 10 | 20072.7 | 106141.4 | 1,320,247 |
| `rlm__single_criterion__rlm_skill_file` | `longbenchpro-rlm` | `rlm_skill_file` | 0.3000 | 0.3000 | 0.0000 | 0.4200 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 230,768 | 58,181 | 3 | 10 | 1625.3 | 9598.3 | 659,205 |
| `rlm__total_score__rlm_skill_file` | `longbenchpro-rlm` | `rlm_skill_file` | 0.2000 | 0.2000 | 0.0000 | 0.3200 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 36,818 | 36,818 | 2 | 10 | 4847.7 | 23389.0 | 663,736 |

**Success@K** is the fraction of rollouts where the judge accepted (`judge_reward` ≥ 0.5) and round count ≤ K. Chat harness uses `num_turns` (assistant generations); RLM uses `root_llm_turns` (root REPL calls). **Mean tok (success)** / **Median tok (success)** aggregate total tokens (input + output) over judge-success rollouts when per-rollout `token_usage` is present (newer runs only; older `summary.json` files may leave these blank).
