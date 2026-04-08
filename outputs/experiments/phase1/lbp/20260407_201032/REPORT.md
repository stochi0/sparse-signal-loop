# phase1/lbp · 20260407_201032

**Benchmark:** LongBench-Pro · Phase 1 (working memory)

*2026-04-07 21:26 UTC*

## Config

```json
{
  "model": "openai/gpt-4.1-mini",
  "judge_model": "openai/gpt-4.1-mini",
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
| `chat__single_criterion__mem_chat` | `longbenchpro` | `chat` | 0.0000 | 0.0000 | 0.0000 | 0.0500 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | — | — | 0 | 5 | 319.3 | 529.9 | 262,001 |
| `chat__total_score__mem_chat` | `longbenchpro` | `chat` | 0.0000 | 0.0000 | 0.0000 | 0.1300 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | — | — | 0 | 5 | 469.3 | 799.9 | 259,176 |
| `rlm__single_criterion__mem_chat` | `longbenchpro-rlm` | `chat` | 0.0000 | 0.0000 | 0.0000 | 0.0500 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | — | — | 0 | 5 | 336.9 | 550.6 | 23,432 |
| `rlm__single_criterion__mem_repl_files` | `longbenchpro-rlm` | `repl_files` | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | — | — | 0 | 5 | 731.5 | 858.7 | 28,993 |
| `rlm__total_score__mem_chat` | `longbenchpro-rlm` | `chat` | 0.2000 | 0.2000 | 0.0000 | 0.2000 | 0.0000 | 0.0000 | 0.0000 | 0.2000 | 16,934 | 16,934 | 1 | 5 | 1072.3 | 1974.3 | 44,509 |
| `rlm__total_score__mem_repl_files` | `longbenchpro-rlm` | `repl_files` | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | — | — | 0 | 5 | 1616.4 | 2085.7 | 82,521 |

**Success@K** is the fraction of rollouts where the judge accepted (`judge_reward` ≥ 0.5) and round count ≤ K. Chat harness uses `num_turns` (assistant generations); RLM uses `root_llm_turns` (root REPL calls). **Mean tok (success)** / **Median tok (success)** aggregate total tokens (input + output) over judge-success rollouts when per-rollout `token_usage` is present (newer runs only; older `summary.json` files may leave these blank).

## RLM vs chat (matched judge feedback)

Within each **feedback** column from the factorial, **chat** is the non-RLM loop; **rlm_mc** / **rlm_rf** are RLM with working memory in chat vs REPL files. **Δ** columns are RLM − chat (positive ⇒ RLM higher). **best** uses the stronger RLM arm; **mean** averages RLM arms that were run.

| Judge feedback | Chat JY | RLM JY (mem chat) | RLM JY (mem repl) | Δ JY best | Δ JY mean | Chat reward | Δ rw best | Δ rw mean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `single_criterion` | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| `total_score` | 0.0000 | 0.2000 | 0.0000 | +0.2000 | +0.1000 | 0.0000 | +0.2000 | +0.1000 |
