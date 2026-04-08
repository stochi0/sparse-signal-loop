# phase2/mini_swe · 20260407_141032

**Benchmark:** phase2/mini_swe

*2026-04-07 16:55 UTC*

## Config

```json
{
  "model": "openai/gpt-4.1-mini",
  "judge_model": "openai/gpt-4.1-mini",
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
| `chat__single_criterion__chat_no_file` | `mini-swe-agent-plus` | `chat_no_file` | 0.4000 | 0.4000 | 0.0000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 636,344 | 636,344 | 2 | 5 | 1616.8 | 1144.4 | 546,960 |
| `chat__single_criterion__chat_system_reinject` | `mini-swe-agent-plus` | `chat_system_reinject` | 0.2000 | 0.2000 | 0.2000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 51,696 | 51,696 | 1 | 5 | 1774.2 | 909.1 | 665,622 |
| `chat__total_score__chat_no_file` | `mini-swe-agent-plus` | `chat_no_file` | 0.4000 | 0.6000 | 0.0000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 419,131 | 419,131 | 2 | 5 | 1554.6 | 1064.8 | 603,420 |
| `chat__total_score__chat_system_reinject` | `mini-swe-agent-plus` | `chat_system_reinject` | 0.0000 | 0.2000 | 0.0000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | — | — | 0 | 5 | 1602.4 | 1042.1 | 633,868 |
| `rlm__single_criterion__rlm_skill_file` | `mini-swe-agent-plus-rlm` | `rlm_skill_file` | 0.2000 | 0.4000 | 0.0000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 219,200 | 219,200 | 1 | 5 | 1733.6 | 1616.2 | 296,913 |
| `rlm__total_score__rlm_skill_file` | `mini-swe-agent-plus-rlm` | `rlm_skill_file` | 0.2000 | 0.2000 | 0.0000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 501,341 | 501,341 | 1 | 5 | 1574.8 | 1462.0 | 351,018 |

**Success@K** is the fraction of rollouts where the judge accepted (`judge_reward` ≥ 0.5) and round count ≤ K. Chat harness uses `num_turns` (assistant generations); RLM uses `root_llm_turns` (root REPL calls). **Mean tok (success)** / **Median tok (success)** aggregate total tokens (input + output) over judge-success rollouts when per-rollout `token_usage` is present (newer runs only; older `summary.json` files may leave these blank).
