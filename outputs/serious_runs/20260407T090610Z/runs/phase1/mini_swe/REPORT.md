# phase1 · mini_swe

**Benchmark:** phase1

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
  "only_repos": null
}
```

## Results

| Cell | Env | Memory | Judge YES | Reward | Err | Task metric | @1 | @2 | @4 | @8 | Mean tok (success) | Median tok (success) | n succ | n | Wall (s) | Roll (s) | Tokens |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `chat__single_criterion__mem_chat` | `mini-swe-agent-plus` | `chat` | 0.7667 | 0.6333 | 0.0000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1,082,272 | 505,509 | 23 | 30 | 2866.3 | 24248.5 | 1,516,681 |
| `chat__total_score__mem_chat` | `mini-swe-agent-plus` | `chat` | 0.8000 | 0.7000 | 0.0000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1,037,016 | 577,165 | 24 | 30 | 2462.6 | 24693.4 | 1,455,311 |
| `rlm__single_criterion__mem_chat` | `mini-swe-agent-plus-rlm` | `chat` | 0.8667 | 0.5667 | 0.0000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1,302,093 | 765,244 | 26 | 30 | 10646.0 | 63670.7 | 1,457,633 |
| `rlm__single_criterion__mem_repl_files` | `mini-swe-agent-plus-rlm` | `repl_files` | 0.8333 | 0.4667 | 0.0000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1,371,481 | 1,060,316 | 25 | 30 | 9181.5 | 56787.0 | 1,623,528 |
| `rlm__total_score__mem_chat` | `mini-swe-agent-plus-rlm` | `chat` | 0.9000 | 0.4667 | 0.0000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1,298,865 | 1,035,012 | 27 | 30 | 8625.5 | 44072.7 | 1,451,797 |
| `rlm__total_score__mem_repl_files` | `mini-swe-agent-plus-rlm` | `repl_files` | 0.9000 | 0.5667 | 0.0333 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1,167,356 | 820,512 | 27 | 30 | 3032.4 | 29375.2 | 1,399,685 |

**Success@K** is the fraction of rollouts where the judge accepted (`judge_reward` ≥ 0.5) and round count ≤ K. Chat harness uses `num_turns` (assistant generations); RLM uses `root_llm_turns` (root REPL calls). **Mean tok (success)** / **Median tok (success)** aggregate total tokens (input + output) over judge-success rollouts when per-rollout `token_usage` is present (newer runs only; older `summary.json` files may leave these blank).

## RLM vs chat (matched judge feedback)

Within each **feedback** column from the factorial, **chat** is the non-RLM loop; **rlm_mc** / **rlm_rf** are RLM with working memory in chat vs REPL files. **Δ** columns are RLM − chat (positive ⇒ RLM higher). **best** uses the stronger RLM arm; **mean** averages RLM arms that were run.

| Judge feedback | Chat JY | RLM JY (mem chat) | RLM JY (mem repl) | Δ JY best | Δ JY mean | Chat reward | Δ rw best | Δ rw mean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `single_criterion` | 0.7667 | 0.8667 | 0.8333 | +0.1000 | +0.0833 | 0.6333 | -0.0667 | -0.1167 |
| `total_score` | 0.8000 | 0.9000 | 0.9000 | +0.1000 | +0.1000 | 0.7000 | -0.1333 | -0.1833 |
