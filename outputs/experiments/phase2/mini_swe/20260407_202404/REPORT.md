# phase2/mini_swe · 20260407_202404

**Benchmark:** phase2/mini_swe

*2026-04-08 07:17 UTC*

## Config

```json
{
  "model": "z-ai/glm-4.7-flash",
  "judge_model": "z-ai/glm-4.7-flash",
  "num_examples": 5,
  "rollouts_per_example": 1,
  "max_concurrent": 1,
  "num_workers": "auto",
  "dataset_name": "PrimeIntellect/SWE-Bench-Verified-Quick",
  "dataset_start_index": 0,
  "max_turns": 80,
  "max_judge_submissions": 8,
  "filter_repos": null,
  "allow_git": false,
  "skip_swebench_install": true,
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
  "phase1_slice": true,
  "only_repos": null,
  "phase2_skill_max_chars": 8000
}
```

## Results

| Cell | Env | Phase 2 arm | Judge YES | Reward | Err | Task metric | @1 | @2 | @4 | @8 | Mean tok (success) | Median tok (success) | n succ | n | Wall (s) | Roll (s) | Tokens |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `chat__single_criterion__chat_no_file` | `mini-swe-agent-plus` | `chat_no_file` | 0.6000 | 0.2000 | 0.2000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 618,254 | 376,336 | 3 | 5 | 4170.4 | 3768.5 | 756,295 |
| `chat__single_criterion__chat_system_reinject` | `mini-swe-agent-plus` | `chat_system_reinject` | 0.4000 | 0.4000 | 0.4000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 227,744 | 227,744 | 2 | 5 | 4438.4 | 4016.1 | 692,153 |
| `chat__total_score__chat_no_file` | `mini-swe-agent-plus` | `chat_no_file` | 0.2000 | 0.4000 | 0.0000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1,284,588 | 1,284,588 | 1 | 5 | 9954.9 | 9411.2 | 1,424,933 |
| `chat__total_score__chat_system_reinject` | `mini-swe-agent-plus` | `chat_system_reinject` | 0.2000 | 0.2000 | 0.0000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 183,868 | 183,868 | 1 | 5 | 7006.7 | 6174.8 | 1,018,199 |
| `rlm__single_criterion__rlm_skill_file` | `mini-swe-agent-plus-rlm` | `rlm_skill_file` | 0.4000 | 0.2000 | 0.4000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1,123,647 | 1,123,647 | 2 | 5 | 7319.8 | 7237.6 | 1,579,633 |
| `rlm__total_score__rlm_skill_file` | `mini-swe-agent-plus-rlm` | `rlm_skill_file` | 0.6000 | 0.2000 | 0.2000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1,413,888 | 878,055 | 3 | 5 | 6287.2 | 5722.1 | 1,138,866 |

**Success@K** is the fraction of rollouts where the judge accepted (`judge_reward` ≥ 0.5) and round count ≤ K. Chat harness uses `num_turns` (assistant generations); RLM uses `root_llm_turns` (root REPL calls). **Mean tok (success)** / **Median tok (success)** aggregate total tokens (input + output) over judge-success rollouts when per-rollout `token_usage` is present (newer runs only; older `summary.json` files may leave these blank).
