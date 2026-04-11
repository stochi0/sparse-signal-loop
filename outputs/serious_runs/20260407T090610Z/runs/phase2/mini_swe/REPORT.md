# phase2 · mini_swe

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
  "dataset_name": "PrimeIntellect/SWE-Bench-Verified-Quick",
  "dataset_start_index": 0,
  "max_turns": 128,
  "max_judge_submissions": 16,
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
  "phase2_skill_max_chars": 16000
}
```

## Results

| Cell | Env | Phase 2 arm | Judge YES | Reward | Err | Task metric | @1 | @2 | @4 | @8 | Mean tok (success) | Median tok (success) | n succ | n | Wall (s) | Roll (s) | Tokens |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `chat__single_criterion__chat_no_file` | `mini-swe-agent-plus` | `chat_no_file` | 0.7000 | 0.6333 | 0.0000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1,345,464 | 808,379 | 21 | 30 | 4885.0 | 35743.3 | 1,521,170 |
| `chat__single_criterion__chat_system_reinject` | `mini-swe-agent-plus` | `chat_system_reinject` | 0.4333 | 0.4333 | 0.3000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 801,589 | 651,376 | 13 | 30 | 7303.0 | 34983.2 | 1,629,301 |
| `chat__total_score__chat_no_file` | `mini-swe-agent-plus` | `chat_no_file` | 0.8000 | 0.6000 | 0.0000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1,353,727 | 706,478 | 24 | 30 | 3608.1 | 26696.0 | 1,524,905 |
| `chat__total_score__chat_system_reinject` | `mini-swe-agent-plus` | `chat_system_reinject` | 0.7667 | 0.6333 | 0.0000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1,394,505 | 919,418 | 23 | 30 | 3877.3 | 31643.0 | 1,471,610 |
| `rlm__single_criterion__rlm_skill_file` | `mini-swe-agent-plus-rlm` | `rlm_skill_file` | 0.7667 | 0.5333 | 0.0000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1,366,150 | 833,712 | 23 | 30 | 10649.1 | 80098.2 | 1,922,550 |
| `rlm__total_score__rlm_skill_file` | `mini-swe-agent-plus-rlm` | `rlm_skill_file` | 0.9667 | 0.5667 | 0.0000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1,556,150 | 1,003,905 | 29 | 30 | 4789.8 | 46206.5 | 1,557,184 |

**Success@K** is the fraction of rollouts where the judge accepted (`judge_reward` ≥ 0.5) and round count ≤ K. Chat harness uses `num_turns` (assistant generations); RLM uses `root_llm_turns` (root REPL calls). **Mean tok (success)** / **Median tok (success)** aggregate total tokens (input + output) over judge-success rollouts when per-rollout `token_usage` is present (newer runs only; older `summary.json` files may leave these blank).
