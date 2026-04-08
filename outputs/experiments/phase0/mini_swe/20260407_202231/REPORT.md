# phase0/mini_swe · 20260407_202231

**Benchmark:** Mini SWE Agent Plus (MSAP)

*2026-04-08 07:39 UTC*

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
  "max_retries": 0
}
```

## Results

| Cell | Env | Judge YES | Reward | Err | Task metric | @1 | @2 | @4 | @8 | Mean tok (success) | Median tok (success) | n succ | n | Wall (s) | Roll (s) | Tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `chat__single_criterion` | `mini-swe-agent-plus` | 0.4000 | 0.4000 | 0.0000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1,872,520 | 1,872,520 | 2 | 5 | 10305.5 | 10210.1 | 2,053,686 |
| `chat__total_score` | `mini-swe-agent-plus` | 0.2000 | 0.4000 | 0.0000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1,095,793 | 1,095,793 | 1 | 5 | 7398.4 | 7311.1 | 1,630,781 |
| `rlm__single_criterion` | `mini-swe-agent-plus-rlm` | 0.0000 | 0.0000 | 0.2000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | — | — | 0 | 5 | 10313.4 | 9961.8 | 1,469,627 |
| `rlm__total_score` | `mini-swe-agent-plus-rlm` | 0.4000 | 0.2000 | 0.0000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1,095,158 | 1,095,158 | 2 | 5 | 12603.7 | 12109.7 | 1,784,458 |

**Success@K** is the fraction of rollouts where the judge accepted (`judge_reward` ≥ 0.5) and round count ≤ K. Chat harness uses `num_turns` (assistant generations); RLM uses `root_llm_turns` (root REPL calls). **Mean tok (success)** / **Median tok (success)** aggregate total tokens (input + output) over judge-success rollouts when per-rollout `token_usage` is present (newer runs only; older `summary.json` files may leave these blank).
