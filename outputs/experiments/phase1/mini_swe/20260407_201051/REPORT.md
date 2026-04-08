# phase1/mini_swe · 20260407_201051

**Benchmark:** Mini SWE Agent Plus · Phase 1 (working memory)

*2026-04-07 23:18 UTC*

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
  "only_repos": null
}
```

## Results

| Cell | Env | Memory | Judge YES | Reward | Err | Task metric | @1 | @2 | @4 | @8 | Mean tok (success) | Median tok (success) | n succ | n | Wall (s) | Roll (s) | Tokens |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `chat__single_criterion__mem_chat` | `mini-swe-agent-plus` | `chat` | 0.2000 | 0.4000 | 0.0000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 46,131 | 46,131 | 1 | 5 | 1792.1 | 1203.9 | 350,712 |
| `chat__total_score__mem_chat` | `mini-swe-agent-plus` | `chat` | 0.4000 | 0.4000 | 0.0000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 372,904 | 372,904 | 2 | 5 | 2557.5 | 1769.6 | 528,985 |
| `rlm__single_criterion__mem_chat` | `mini-swe-agent-plus-rlm` | `chat` | 0.0000 | 0.0000 | 0.0000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | — | — | 0 | 5 | 2045.4 | 1883.3 | 690,760 |
| `rlm__single_criterion__mem_repl_files` | `mini-swe-agent-plus-rlm` | `repl_files` | 0.0000 | 0.2000 | 0.0000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | — | — | 0 | 5 | 2130.0 | 1909.1 | 731,981 |
| `rlm__total_score__mem_chat` | `mini-swe-agent-plus-rlm` | `chat` | 0.0000 | 0.2000 | 0.0000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | — | — | 0 | 5 | 1404.2 | 1042.0 | 213,084 |
| `rlm__total_score__mem_repl_files` | `mini-swe-agent-plus-rlm` | `repl_files` | 0.0000 | 0.4000 | 0.0000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | — | — | 0 | 5 | 1332.1 | 1140.6 | 279,443 |

**Success@K** is the fraction of rollouts where the judge accepted (`judge_reward` ≥ 0.5) and round count ≤ K. Chat harness uses `num_turns` (assistant generations); RLM uses `root_llm_turns` (root REPL calls). **Mean tok (success)** / **Median tok (success)** aggregate total tokens (input + output) over judge-success rollouts when per-rollout `token_usage` is present (newer runs only; older `summary.json` files may leave these blank).

## RLM vs chat (matched judge feedback)

Within each **feedback** column from the factorial, **chat** is the non-RLM loop; **rlm_mc** / **rlm_rf** are RLM with working memory in chat vs REPL files. **Δ** columns are RLM − chat (positive ⇒ RLM higher). **best** uses the stronger RLM arm; **mean** averages RLM arms that were run.

| Judge feedback | Chat JY | RLM JY (mem chat) | RLM JY (mem repl) | Δ JY best | Δ JY mean | Chat reward | Δ rw best | Δ rw mean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `single_criterion` | 0.2000 | 0.0000 | 0.0000 | -0.2000 | -0.2000 | 0.4000 | -0.2000 | -0.3000 |
| `total_score` | 0.4000 | 0.0000 | 0.0000 | -0.4000 | -0.4000 | 0.4000 | 0.0000 | -0.1000 |
