# phase0/mini_swe · 20260407_200840

**Benchmark:** Mini SWE Agent Plus (MSAP)

*2026-04-07 22:29 UTC*

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
  "max_retries": 0
}
```

## Results

| Cell | Env | Judge YES | Reward | Err | Task metric | @1 | @2 | @4 | @8 | Mean tok (success) | Median tok (success) | n succ | n | Wall (s) | Roll (s) | Tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `chat__single_criterion` | `mini-swe-agent-plus` | 0.4000 | 0.0000 | 0.0000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 646,866 | 646,866 | 2 | 5 | 2223.8 | 2140.5 | 875,750 |
| `chat__total_score` | `mini-swe-agent-plus` | 0.0000 | 0.2000 | 0.0000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | — | — | 0 | 5 | 2352.7 | 2263.6 | 780,117 |
| `rlm__single_criterion` | `mini-swe-agent-plus-rlm` | 0.2000 | 0.0000 | 0.0000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 84,833 | 84,833 | 1 | 5 | 1950.3 | 1171.8 | 368,413 |
| `rlm__total_score` | `mini-swe-agent-plus-rlm` | 0.0000 | 0.0000 | 0.0000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | — | — | 0 | 5 | 1878.3 | 1049.5 | 325,857 |

**Success@K** is the fraction of rollouts where the judge accepted (`judge_reward` ≥ 0.5) and round count ≤ K. Chat harness uses `num_turns` (assistant generations); RLM uses `root_llm_turns` (root REPL calls). **Mean tok (success)** / **Median tok (success)** aggregate total tokens (input + output) over judge-success rollouts when per-rollout `token_usage` is present (newer runs only; older `summary.json` files may leave these blank).
