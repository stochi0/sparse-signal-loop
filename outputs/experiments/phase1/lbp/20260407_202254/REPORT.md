# phase1/lbp · 20260407_202254

**Benchmark:** LongBench-Pro · Phase 1 (working memory)

*2026-04-08 01:58 UTC*

## Config

```json
{
  "model": "z-ai/glm-4.7-flash",
  "judge_model": "z-ai/glm-4.7-flash",
  "num_examples": 5,
  "rollouts_per_example": 1,
  "max_concurrent": 2,
  "num_workers": "auto",
  "seed": 42,
  "language": "English",
  "dataset_start_index": 0,
  "token_length": "all",
  "difficulty": "all",
  "thinking": false,
  "include_env_tips": false,
  "prompt_in_context_file": false,
  "max_turns_chat": 8,
  "max_turns_rlm": 30,
  "max_judge_submissions": 8,
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
  "shuffle": false,
  "phase1_slice": true
}
```

## Results

| Cell | Env | Memory | Judge YES | Reward | Err | Task metric | @1 | @2 | @4 | @8 | Mean tok (success) | Median tok (success) | n succ | n | Wall (s) | Roll (s) | Tokens |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `chat__single_criterion__mem_chat` | `longbenchpro` | `chat` | 0.2000 | 0.2000 | 0.0000 | 0.3200 | 0.0000 | 0.2000 | 0.2000 | 0.2000 | 80,005 | 80,005 | 1 | 5 | 7018.9 | 13291.2 | 301,306 |
| `chat__total_score__mem_chat` | `longbenchpro` | `chat` | 0.2000 | 0.2000 | 0.0000 | 0.3200 | 0.0000 | 0.2000 | 0.2000 | 0.2000 | 70,135 | 70,135 | 1 | 5 | 5889.5 | 11407.2 | 317,104 |
| `rlm__single_criterion__mem_chat` | `longbenchpro-rlm` | `chat` | 0.0000 | 0.0000 | 0.6000 | 0.1600 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | — | — | 0 | 5 | 1237.5 | 2341.7 | 141,996 |
| `rlm__single_criterion__mem_repl_files` | `longbenchpro-rlm` | `repl_files` | 0.2000 | 0.2000 | 0.4000 | 0.2000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 70,367 | 70,367 | 1 | 5 | 2022.3 | 3902.6 | 139,564 |
| `rlm__total_score__mem_chat` | `longbenchpro-rlm` | `chat` | 0.0000 | 0.0000 | 0.4000 | 0.0800 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | — | — | 0 | 5 | 2036.5 | 3757.2 | 100,708 |
| `rlm__total_score__mem_repl_files` | `longbenchpro-rlm` | `repl_files` | 0.2000 | 0.2000 | 0.4000 | 0.2000 | 0.0000 | 0.0000 | 0.0000 | 0.2000 | 26,909 | 26,909 | 1 | 5 | 1889.3 | 3256.7 | 149,983 |

**Success@K** is the fraction of rollouts where the judge accepted (`judge_reward` ≥ 0.5) and round count ≤ K. Chat harness uses `num_turns` (assistant generations); RLM uses `root_llm_turns` (root REPL calls). **Mean tok (success)** / **Median tok (success)** aggregate total tokens (input + output) over judge-success rollouts when per-rollout `token_usage` is present (newer runs only; older `summary.json` files may leave these blank).

## RLM vs chat (matched judge feedback)

Within each **feedback** column from the factorial, **chat** is the non-RLM loop; **rlm_mc** / **rlm_rf** are RLM with working memory in chat vs REPL files. **Δ** columns are RLM − chat (positive ⇒ RLM higher). **best** uses the stronger RLM arm; **mean** averages RLM arms that were run.

| Judge feedback | Chat JY | RLM JY (mem chat) | RLM JY (mem repl) | Δ JY best | Δ JY mean | Chat reward | Δ rw best | Δ rw mean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `single_criterion` | 0.2000 | 0.0000 | 0.2000 | 0.0000 | -0.1000 | 0.2000 | 0.0000 | -0.1000 |
| `total_score` | 0.2000 | 0.0000 | 0.2000 | 0.0000 | -0.1000 | 0.2000 | 0.0000 | -0.1000 |
