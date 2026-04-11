# phase0 · mini_swe

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
  "max_retries": 0
}
```

## Results

| Cell | Env | Judge YES | Reward | Err | Task metric | @1 | @2 | @4 | @8 | Mean tok (success) | Median tok (success) | n succ | n | Wall (s) | Roll (s) | Tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `chat__single_criterion` | `mini-swe-agent-plus` | 0.6333 | 0.5000 | 0.0667 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1,262,807 | 870,496 | 19 | 30 | 7529.3 | 47436.3 | 2,250,750 |
| `chat__total_score` | `mini-swe-agent-plus` | 0.3333 | 0.4333 | 0.0000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 2,246,296 | 2,261,603 | 10 | 30 | 6816.9 | 51969.1 | 3,011,184 |
| `rlm__single_criterion` | `mini-swe-agent-plus-rlm` | 0.7333 | 0.5333 | 0.0000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1,780,399 | 1,444,502 | 22 | 30 | 7613.5 | 74053.4 | 1,957,730 |
| `rlm__total_score` | `mini-swe-agent-plus-rlm` | 0.8667 | 0.5667 | 0.0000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1,718,996 | 1,495,054 | 26 | 30 | 10648.1 | 82844.9 | 1,864,276 |

**Success@K** is the fraction of rollouts where the judge accepted (`judge_reward` ≥ 0.5) and round count ≤ K. Chat harness uses `num_turns` (assistant generations); RLM uses `root_llm_turns` (root REPL calls). **Mean tok (success)** / **Median tok (success)** aggregate total tokens (input + output) over judge-success rollouts when per-rollout `token_usage` is present (newer runs only; older `summary.json` files may leave these blank).
