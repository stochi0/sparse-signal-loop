# Sparse Signals, Real Constraints, and What the Phases Actually Taught Us

Most projects claim they are "hypothesis-driven." In practice, many are tooling-driven: we build infrastructure, then run what that infrastructure makes easy, then post-rationalize the lessons.

This project went the other way by accident and then by design.

The commit arc shows a clean progression:

- shared experiment runners and phase schema scaffolding,
- judge and reporting primitives (`Judge YES`, `Success@K`, task metrics),
- phase-specific interventions (memory modes in Phase 1, skill-file style in Phase 2),
- and finally, consolidated markdown outputs that make comparisons legible.

That order matters. It means we now have enough structure to ask one high-leverage question without being distracted by every possible extension.

## The question that actually decides the direction

> If judge feedback is reduced from total score to a single violated criterion, does refinement quality change, and does an RLM harness extract more value from that sparse signal than vanilla iterative refinement?

This is the Axis 1 x Axis 3 intersection in concrete form:

- Axis 1: hard-to-verify settings where direct reward is weak or delayed.
- Axis 3: refinement mechanics and harness behavior over trajectories.

In semi-verifiable tasks, hard verification often manifests as feedback sparsity. So the proper first experiment is a 2x2:

- Feedback format: `total_score` vs `single_criterion`
- Harness style: non-RLM iterative chat loop vs RLM harness

The reason this question is so powerful is simple: whichever way it resolves, it tells us where to invest.

- If RLM clearly wins under sparse feedback, the harness hypothesis is alive and worth scaling.
- If chat and RLM perform similarly, feedback format likely explains most gains.
- If chat is stronger under sparse feedback, the current RLM implementation is not yet delivering its intended advantage.

Any of those outcomes is useful. Ambiguous framing is what costs time, not negative results.

---

## Why this blog is long on metrics and short on mythology

This post reads directly from experiment reports in `outputs` and `archive`, not from handpicked examples. The goal is not to manufacture optimism. The goal is to identify which claims survive contact with numbers.

Sources used:

- `outputs/outputs/experiments/phase0/lbp/20260407_200743/REPORT.md`
- `archive/outputs0/experiments/phase1/lbp/20260407_055028/REPORT.md`
- `outputs/outputs/experiments/phase2/lbp/20260407_140919/REPORT.md`
- `archive/outputs0/experiments/phase0/mini_swe/20260405_213310/REPORT.md`
- `archive/outputs0/experiments/phase1/mini_swe/20260406_205705/REPORT.md`
- `outputs/outputs/experiments/phase2/mini_swe/20260407_144025/REPORT.md`

---

## Experimental context, in plain terms

Before digging into phase-by-phase outcomes, it helps to restate the harnesses because terminology can hide the actual behavioral difference.

### Non-RLM iterative refinement (chat loop)

The model sees a growing conversation:

1. user task,
2. model answer,
3. judge feedback,
4. model revision,
5. repeat.

It has no explicit concept of "trajectory planning." It just reacts to transcript state.

### RLM harness

The model is expected to act like a reasoning loop machine:

- it is aware of turn budget,
- it can externalize memory/plans,
- it is supposed to treat judge output as strategic signal,
- and update search policy, not merely patch one local error.

So the intended difference is not "more turns." The intended difference is control policy over turns.

---

## Metric semantics and why they matter

There are several numbers in each table. They are not interchangeable.

### `Judge YES` (primary endpoint)

This is the strict acceptance rate. If a harness does not move this metric, it is not delivering end-to-end success, no matter how much intermediate progress it appears to make.

### `Reward` (secondary endpoint)

Useful when it tracks partial progress, but can diverge from strict pass/fail. A non-zero reward with zero `Judge YES` is often a warning sign: local optimization without final closure.

### `Task metric` (LBP continuous quality)

Valuable for distinguishing "how good" among non-accepted outputs. But if acceptance is the operational objective, task metric cannot replace `Judge YES`.

### `Success@K`

Budget-sensitive success. It tells us not only if a system works, but if it works early enough in the trajectory to be practical.

### Cost metrics (`Tokens`, `Wall`, `Roll`)

Important because a harness that is 3x more expensive needs a quality delta to justify itself. Cost efficiency is useful only if it preserves or improves outcome quality.

---

## Phase 0: baseline factorial and the first strong contradiction

### LongBench-Pro baseline (Phase 0)

Source: `outputs/outputs/experiments/phase0/lbp/20260407_200743/REPORT.md`

Configuration highlights:

- model and judge both `openai/gpt-4.1-mini`
- `num_examples = 5`
- `max_turns_chat = 8`
- `max_turns_rlm = 30`

Observed:

- `chat__single_criterion`: Judge YES `0.40`, Reward `0.40`, Task metric `0.5581`
- `chat__total_score`: Judge YES `0.40`, Reward `0.40`, Task metric `0.4503`
- `rlm__single_criterion`: Judge YES `0.00`, Reward `0.00`, Task metric `0.1180`
- `rlm__total_score`: Judge YES `0.20`, Reward `0.20`, Task metric `0.0667`

What matters:

- In chat, sparse feedback improves continuous quality (`0.5581` vs `0.4503`) at equal acceptance.
- In RLM, sparse feedback is worse than total-score on acceptance (`0.00` vs `0.20`).
- Chat used significantly more tokens, yet still produced better acceptance behavior.

This is the first contradiction to the naive harness thesis. If sparse feedback were naturally a better fit for RLM, this table should have hinted in that direction. It did not.

### Mini-SWE baseline (Phase 0, archive)

Source: `archive/outputs0/experiments/phase0/mini_swe/20260405_213310/REPORT.md`

Observed (`n=1`):

- all four cells are `0.00` Judge YES.

Interpretation:

- no discriminative signal at this sample size.
- useful mostly as a reminder that Mini-SWE is harsher and can saturate at zero without enough runs or adapted policies.

---

## Phase 1: memory substrate as a control-policy lever

Phase 1 introduces memory-mode interventions and asks whether feedback effects are robust to memory representation.

### LBP Phase 1 (archive)

Source: `archive/outputs0/experiments/phase1/lbp/20260407_055028/REPORT.md`

Important caveat:

- model stack differs from Phase 0/2 (`z-ai/glm-4.7` policy, `glm-4.7-flash` judge),
- `n=1` per arm.

Observed:

- `chat__single_criterion__mem_chat`: Judge YES `1.00`
- `chat__total_score__mem_chat`: Judge YES `1.00`
- `rlm__single_criterion__mem_chat`: Judge YES `1.00`
- `rlm__single_criterion__mem_repl_files`: Judge YES `1.00`
- `rlm__total_score__mem_chat`: Judge YES `0.00`
- `rlm__total_score__mem_repl_files`: Judge YES `1.00`

Interpretation:

- For RLM, memory substrate can flip outcome under the same feedback format.
- Sparse feedback appears robust in this tiny slice.
- Dense feedback with chat memory fails while dense feedback with repl-file memory succeeds.

This is a major mechanistic clue: if results can flip by memory representation, then "harness quality" is not one scalar property; it is heavily implementation-bound.

### Mini-SWE Phase 1 (archive)

Source: `archive/outputs0/experiments/phase1/mini_swe/20260406_205705/REPORT.md`

Observed:

- `chat__total_score__mem_chat`: Judge YES `0.00`
- `rlm__total_score__mem_chat`: Judge YES `0.00`

Interpretation:

- no evidence that this memory intervention is sufficient for Mini-SWE at this scale.
- we cannot infer sparse-vs-dense effects here because this report slice does not include sparse cells.

---

## Phase 2: strategy externalization and skill-file behavior

Phase 2 introduces skill-file and reinjection structures intended to improve strategic consistency over trajectories.

### LBP Phase 2

Source: `outputs/outputs/experiments/phase2/lbp/20260407_140919/REPORT.md`

Observed (`n=5`):

- `chat__single_criterion__chat_no_file`: Judge YES `0.00`
- `chat__single_criterion__chat_system_reinject`: Judge YES `0.00`
- `chat__total_score__chat_no_file`: Judge YES `0.00`
- `chat__total_score__chat_system_reinject`: Judge YES `0.20`
- `rlm__single_criterion__rlm_skill_file`: Judge YES `0.00`
- `rlm__total_score__rlm_skill_file`: Judge YES `0.00`

Additional context:

- chat token usage is very high in this run (roughly `243k`-`251k` per arm),
- RLM token usage is much lower (`15k`-`52k`),
- but lower cost does not recover acceptance.

Interpretation:

- most cells are in failure regime.
- one chat dense arm escapes to `0.20`, still weak.
- skill-file injection by itself does not produce a consistent acceptance lift.

### Mini-SWE Phase 2

Source: `outputs/outputs/experiments/phase2/mini_swe/20260407_144025/REPORT.md`

Observed (`n=5`):

- chat sparse:
  - `chat_no_file`: Judge YES `0.40`, Reward `0.60`
  - `chat_system_reinject`: Judge YES `0.60`, Reward `0.40`
- chat dense:
  - `chat_no_file`: Judge YES `0.40`, Reward `0.40`
  - `chat_system_reinject`: Judge YES `0.40`, Reward `0.40`
- RLM skill-file:
  - sparse: Judge YES `0.00`, Reward `0.40`
  - dense: Judge YES `0.00`, Reward `0.60`

Interpretation:

- chat gets a sparse-feedback bump in at least one arm (`0.60` vs dense `0.40`).
- RLM accumulates reward without converting to strict acceptance.
- this confirms a repeat failure mode: partial progress that never closes acceptance criteria.

---

## The answer, stated directly

### Q1: Does replacing total score with single violated criterion change refinement quality?

Yes, but not uniformly.

- chat loops show neutral-to-positive movement under sparse feedback across multiple slices.
- RLM does not show a stable sparse-feedback advantage in current runs.

### Q2: Does RLM extract more value from sparse feedback than vanilla iterative refinement?

Current answer: **no**.

Across the available evidence, there is no repeatable sparse-cell advantage for RLM over chat.

### Q3: Is the RLM harness still doing something different?

Likely yes at process level, but not yet at objective completion level.

- often lower token consumption,
- sometimes non-zero reward despite zero acceptance,
- implying search activity without final criteria closure.

---

## Why this pattern is plausible (and not surprising)

There are concrete technical reasons this can happen.

### 1) Sparse feedback is informative but low-bandwidth

A single violated criterion can focus attention, but it can also under-specify the repair path. A reactive chat loop may still perform well because it naturally overfits to immediate textual signals. RLM may require stronger internal abstractions to capitalize on sparse signals.

### 2) Policy mismatch between exploration and closure

RLM can spend trajectory budget exploring states and collecting structure, but if its termination/commit behavior is weak, it misses final acceptance thresholds.

### 3) Memory substrate defines effective state space

The Phase 1 LBP split (`mem_chat` failure vs `mem_repl_files` success for one dense arm) suggests representational effects matter more than generic "RLM vs non-RLM" framing.

### 4) Reward and acceptance are related but not equivalent

When reward rises without Judge YES, optimization can drift toward "looks better" rather than "passes criterion bundle."

### 5) Small samples amplify narrative risk

With `n=1` and `n=5`, dramatic stories are easy and usually wrong. The right interpretation is directional, not definitive.

---

## Threats to validity you should keep in mind

This section is explicit because negative results are only useful when caveats are surfaced.

- **Sample-size fragility:** most cells are too small for strong inference.
- **Model/judge inconsistency across phases:** Phase 1 LBP used GLM stack, others used GPT-4.1-mini.
- **Benchmark heterogeneity:** LBP and Mini-SWE represent different failure surfaces.
- **Budget asymmetry risk:** turn caps differ by harness type; token behavior also differs.
- **Prompt/control drift across phases:** interventions overlap with feedback effects.

These do not invalidate the observed pattern. They limit confidence interval width.

---

## What would count as convincing evidence next

To settle this efficiently, we should run a decisive replication, not a sprawling expansion.

### Proposed experiment spec (minimum credible design)

1. Single benchmark first (LBP), fixed model and fixed judge.
2. Full 2x2 grid with `n >= 50` examples per cell.
3. Matched budget protocols:
   - equalized turn budget policy,
   - and token-normalized secondary analysis.
4. Structured logs for each turn:
   - violated criterion id,
   - whether criterion identity changed from previous turn,
   - whether candidate answer class changed or only wording changed.
5. Primary endpoint:
   - `Judge YES` difference between sparse RLM and sparse chat.
6. Secondary endpoints:
   - conversion ratio from partial reward to Judge YES,
   - Success@K profile shape,
   - token-adjusted acceptance efficiency.

### What outcomes would mean

- **Sparse RLM > sparse chat:** harness hypothesis gains strong support.
- **Sparse RLM ~= sparse chat:** feedback format explains gains, harness adds little.
- **Sparse RLM < sparse chat:** current harness policy likely flawed; prioritize policy redesign over scaling.

---

## Practical redesign bets if RLM remains weak

If replication confirms current pattern, these are the highest-value redesign directions:

### Criterion-tracking policy layer

Explicitly track criterion history and unresolved failure chains, not just latest feedback text.

### Closure-focused turn budgeting

Reserve late turns for "acceptance closure" attempts instead of continuous exploration.

### Conversion-aware objective

Add training or prompting pressure on converting partial reward trajectories into accepted outcomes.

### Memory abstraction contracts

Standardize how state is externalized in memory files so strategic state is queryable and consistent.

### Critic diversity

Use alternate critics for intermediate shaping, but keep final judge fixed to avoid overfitting to one feedback style.

---

## Relation to continual learning: harness ceilings and parametric compounding

A separate line of argument—sketched well in [continual-learning.md](continual-learning.md) (Lichkovski on in-weights continual learning vs harness memory)—helps explain *why* our sparse-feedback and harness results might line up the way they do.

### The claim in brief

Harness-based memory (skill files, markdown banks, growing “skill trees,” RLM external state) has real advantages: inspectability, editability, and strong in-context use of whatever gets retrieved. But as that external bank grows, you hit **diminishing returns and sometimes degradation**: context rot, retrieval errors, and the fact that the **underlying model’s per-forward-pass “intelligence” is fixed**. You are asking the same intrinsic model to operate over an ever larger, noisier external library. **Parametric** learning, by contrast, changes what each forward pass *is*—representations compress and recombine—so compounding is at least *possible* in principle.

### How that maps onto these experiments

**1. Phase 2 skill / reinjection without a conversion breakthrough**

We added Phase 2 structure (skill-file arms, system reinjection) precisely to externalize strategy. On LBP Phase 2, most cells still collapsed to near-zero `Judge YES`; on Mini-SWE Phase 2, chat sometimes gained from sparse feedback and reinjection, while RLM still showed **reward without acceptance**. That pattern is consistent with the continual-learning critique: **more harness surface area does not automatically increase end-to-end capability** if the bottleneck is closure, retrieval, or context budget—not missing markdown. Growing a “skill tree” in the harness can yield **local** improvements (prompting, partial reward) without **global** lift on the strict judge, i.e. diminishing marginal returns at the system level.

**2. Phase 1 memory splits (chat vs REPL files)**

When RLM outcomes **flip** depending on whether memory lives in chat vs repl-file form, we are seeing the harness not as a neutral pipe but as a **representation and routing problem**. That matches the blog’s point that compositionality over external knowledge eventually reduces to **how good the retriever and memory contract are**—and that ceiling is structural unless the policy model changes.

**3. Sparse feedback as low bandwidth**

Single-criterion feedback is intentionally sparse. A harness must route that signal through turns, memory, and possibly skill files. If the **fixed** model does not automatically reorganize strategy (the “automaticity” argument), sparse feedback may help **reactive** chat loops more than **structured** RLM loops that depend on consistent state updates. So the 2×2 result (chat often fine; RLM not clearly winning on sparse) is compatible with: **sparse signal + complex harness = more ways to drop the signal**, unless the harness is nearly perfect or the weights absorb the skill.

**4. Why “RLM uses fewer tokens” is not enough**

Token efficiency is real, but if the model’s **effective** intelligence per step is fixed, cheaper trajectories are still bounded by that ceiling. The continual-learning framing says the compounding bet is **parametric** (or hybrid with real weight updates), not “infinite SKILL.md.” Our runs do not prove that thesis in the abstract; they **rhyme** with it: partial progress without `Judge YES` looks like **activity without compounding into the kind of closure that strict judges require**.

### What we should not overclaim

This does **not** mean harness-only approaches are useless, or that RLMs cannot work. Lichkovski explicitly leaves room for **agentic training with a harness** as a path that still touches weights. It means: **if our goal is strict acceptance and scalable adaptation, external skill growth alone is a risky primary bet**—consistent with seeing harness-heavy arms fail to dominate sparse-feedback cells in these results.

---

## A note on interpretation discipline

The tempting narrative is:

"RLM is early; just scale and it will win."

The responsible narrative from current evidence is:

"RLM behavior differs in process, but we do not yet see reliable sparse-signal extraction advantages on strict acceptance."

That distinction is crucial. Many projects lose months by treating process novelty as proof of outcome superiority.

---

## Conclusion: what these phases really bought us

The phases were not wasted effort. They delivered exactly what early research infra should deliver: falsifiable constraints.

What we now know:

- Sparse feedback can improve refinement behavior, especially in vanilla chat loops.
- Current RLM harness variants do not yet show consistent sparse-feedback superiority.
- Memory representation and policy closure appear to be key bottlenecks.
- Cost efficiency alone is not meaningful without acceptance conversion.

What to do next is no longer ambiguous:

- run one decisive, powered, instrumented 2x2 replication,
- then either validate the harness thesis or pivot quickly to conversion-centric redesign.

That is the real value of this phase stack: less mythology, more decision velocity.



https://x.com/willccbb/status/2041625336576929931?s=20