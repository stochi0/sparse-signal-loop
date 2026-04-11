# phase1 · lbp

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
  "seed": 42,
  "language": "English",
  "dataset_start_index": 0,
  "token_length": "all",
  "difficulty": "all",
  "thinking": false,
  "include_env_tips": false,
  "prompt_in_context_file": false,
  "max_turns_chat": 32,
  "max_turns_rlm": 64,
  "max_judge_submissions": 16,
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
| `chat__single_criterion__mem_chat` | `longbenchpro` | `chat` | 0.3000 | 0.3000 | 0.0000 | 0.4300 | 0.0000 | 0.1000 | 0.1000 | 0.2000 | 625,059 | 330,492 | 3 | 10 | 16357.2 | 72103.3 | 1,682,959 |
| `chat__total_score__mem_chat` | `longbenchpro` | `chat` | 0.4000 | 0.4000 | 0.0000 | 0.4800 | 0.2000 | 0.2000 | 0.3000 | 0.4000 | 144,590 | 143,096 | 4 | 10 | 13218.9 | 64038.1 | 1,380,704 |
| `rlm__single_criterion__mem_chat` | `longbenchpro-rlm` | `chat` | 0.1000 | 0.1000 | 0.0000 | 0.2800 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 42,420 | 42,420 | 1 | 10 | 5638.4 | 20958.4 | 646,398 |
| `rlm__single_criterion__mem_repl_files` | `longbenchpro-rlm` | `repl_files` | 0.1000 | 0.1000 | 0.0000 | 0.2200 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 35,974 | 35,974 | 1 | 10 | 4102.4 | 17900.6 | 774,170 |
| `rlm__total_score__mem_chat` | `longbenchpro-rlm` | `chat` | 0.2000 | 0.2000 | 0.0000 | 0.3800 | 0.0000 | 0.0000 | 0.0000 | 0.1000 | 40,933 | 40,933 | 2 | 10 | 2235.8 | 13706.0 | 637,206 |
| `rlm__total_score__mem_repl_files` | `longbenchpro-rlm` | `repl_files` | 0.2000 | 0.2000 | 0.0000 | 0.4500 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 163,718 | 163,718 | 2 | 10 | 2864.5 | 15147.0 | 643,555 |

**Success@K** is the fraction of rollouts where the judge accepted (`judge_reward` ≥ 0.5) and round count ≤ K. Chat harness uses `num_turns` (assistant generations); RLM uses `root_llm_turns` (root REPL calls). **Mean tok (success)** / **Median tok (success)** aggregate total tokens (input + output) over judge-success rollouts when per-rollout `token_usage` is present (newer runs only; older `summary.json` files may leave these blank).

## RLM vs chat (matched judge feedback)

Within each **feedback** column from the factorial, **chat** is the non-RLM loop; **rlm_mc** / **rlm_rf** are RLM with working memory in chat vs REPL files. **Δ** columns are RLM − chat (positive ⇒ RLM higher). **best** uses the stronger RLM arm; **mean** averages RLM arms that were run.

| Judge feedback | Chat JY | RLM JY (mem chat) | RLM JY (mem repl) | Δ JY best | Δ JY mean | Chat reward | Δ rw best | Δ rw mean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `single_criterion` | 0.3000 | 0.1000 | 0.1000 | -0.2000 | -0.2000 | 0.3000 | -0.2000 | -0.2000 |
| `total_score` | 0.4000 | 0.2000 | 0.2000 | -0.2000 | -0.2000 | 0.4000 | -0.2000 | -0.2000 |
