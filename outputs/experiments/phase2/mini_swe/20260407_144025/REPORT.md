# phase2/mini_swe · 20260407_144025

**Benchmark:** phase2/mini_swe

*2026-04-07 17:29 UTC*

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
| `chat__single_criterion__chat_no_file` | `mini-swe-agent-plus` | `chat_no_file` | 0.4000 | 0.6000 | 0.0000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 388,170 | 388,170 | 2 | 5 | 1819.2 | 1236.0 | 560,660 |
| `chat__single_criterion__chat_system_reinject` | `mini-swe-agent-plus` | `chat_system_reinject` | 0.6000 | 0.4000 | 0.0000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 476,789 | 535,851 | 3 | 5 | 1683.7 | 1247.9 | 502,416 |
| `chat__total_score__chat_no_file` | `mini-swe-agent-plus` | `chat_no_file` | 0.4000 | 0.4000 | 0.0000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 498,658 | 498,658 | 2 | 5 | 1463.4 | 1025.2 | 579,787 |
| `chat__total_score__chat_system_reinject` | `mini-swe-agent-plus` | `chat_system_reinject` | 0.4000 | 0.4000 | 0.0000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 234,836 | 234,836 | 2 | 5 | 1611.7 | 1073.5 | 633,635 |
| `rlm__single_criterion__rlm_skill_file` | `mini-swe-agent-plus-rlm` | `rlm_skill_file` | 0.0000 | 0.4000 | 0.0000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | — | — | 0 | 5 | 1670.3 | 1225.8 | 230,265 |
| `rlm__total_score__rlm_skill_file` | `mini-swe-agent-plus-rlm` | `rlm_skill_file` | 0.0000 | 0.6000 | 0.0000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | — | — | 0 | 5 | 1883.6 | 1389.5 | 384,201 |

**Success@K** is the fraction of rollouts where the judge accepted (`judge_reward` ≥ 0.5) and round count ≤ K. Chat harness uses `num_turns` (assistant generations); RLM uses `root_llm_turns` (root REPL calls). **Mean tok (success)** / **Median tok (success)** aggregate total tokens (input + output) over judge-success rollouts when per-rollout `token_usage` is present (newer runs only; older `summary.json` files may leave these blank).
