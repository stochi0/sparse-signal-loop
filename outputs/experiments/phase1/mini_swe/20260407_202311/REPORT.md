# phase1/mini_swe · 20260407_202311

**Benchmark:** Mini SWE Agent Plus · Phase 1 (working memory)

*2026-04-08 09:08 UTC*

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
  "only_repos": null
}
```

## Results

| Cell | Env | Memory | Judge YES | Reward | Err | Task metric | @1 | @2 | @4 | @8 | Mean tok (success) | Median tok (success) | n succ | n | Wall (s) | Roll (s) | Tokens |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `chat__single_criterion__mem_chat` | `mini-swe-agent-plus` | `chat` | 0.2000 | 0.0000 | 0.0000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 198,494 | 198,494 | 1 | 5 | 5970.0 | 5376.5 | 1,178,201 |
| `chat__total_score__mem_chat` | `mini-swe-agent-plus` | `chat` | 0.6000 | 0.4000 | 0.0000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 511,031 | 575,909 | 3 | 5 | 5565.8 | 4802.8 | 618,970 |
| `rlm__single_criterion__mem_chat` | `mini-swe-agent-plus-rlm` | `chat` | 0.2000 | 0.0000 | 0.2000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 662,560 | 662,560 | 1 | 5 | 11529.7 | 11122.7 | 930,144 |
| `rlm__single_criterion__mem_repl_files` | `mini-swe-agent-plus-rlm` | `repl_files` | 0.2000 | 0.0000 | 0.6000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1,308,505 | 1,308,505 | 1 | 5 | 7344.2 | 7299.4 | 782,914 |
| `rlm__total_score__mem_chat` | `mini-swe-agent-plus-rlm` | `chat` | 0.2000 | 0.2000 | 0.6000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 294,781 | 294,781 | 1 | 5 | 7690.1 | 7615.7 | 1,124,205 |
| `rlm__total_score__mem_repl_files` | `mini-swe-agent-plus-rlm` | `repl_files` | 0.2000 | 0.2000 | 0.6000 | — | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 990,005 | 990,005 | 1 | 5 | 7701.2 | 7592.3 | 851,977 |

**Success@K** is the fraction of rollouts where the judge accepted (`judge_reward` ≥ 0.5) and round count ≤ K. Chat harness uses `num_turns` (assistant generations); RLM uses `root_llm_turns` (root REPL calls). **Mean tok (success)** / **Median tok (success)** aggregate total tokens (input + output) over judge-success rollouts when per-rollout `token_usage` is present (newer runs only; older `summary.json` files may leave these blank).

## RLM vs chat (matched judge feedback)

Within each **feedback** column from the factorial, **chat** is the non-RLM loop; **rlm_mc** / **rlm_rf** are RLM with working memory in chat vs REPL files. **Δ** columns are RLM − chat (positive ⇒ RLM higher). **best** uses the stronger RLM arm; **mean** averages RLM arms that were run.

| Judge feedback | Chat JY | RLM JY (mem chat) | RLM JY (mem repl) | Δ JY best | Δ JY mean | Chat reward | Δ rw best | Δ rw mean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `single_criterion` | 0.2000 | 0.2000 | 0.2000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| `total_score` | 0.6000 | 0.2000 | 0.2000 | -0.4000 | -0.4000 | 0.4000 | -0.2000 | -0.2000 |
