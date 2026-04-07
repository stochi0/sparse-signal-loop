"""
LongBench-Pro long-context environment.

The full context and question are delivered in the user message. With ``in_loop_judge``,
an LLM judge runs **during** the rollout (after each assistant turn via ``verifiers.MultiTurnEnv``);
otherwise judging is rubric-only at trajectory end (single-turn).

Dataset: caskcsg/LongBench-Pro
Reference: https://github.com/caskcsg/longcontext/tree/main/LongBench-Pro
"""

from __future__ import annotations

import json
import random
from typing import Any, Literal

import verifiers as vf
from datasets import load_dataset
from longbenchpro_prompts import (
    JudgeFeedbackMode,
    Phase1MemoryMode,
    Phase2SkillMode,
    extract_phase2_skill_block,
    lbp_judge_prompt_for_mode,
    phase1_working_memory_suffix,
    phase2_skill_suffix,
    resolve_phase1_lbp_filters,
)
from longbenchpro_task_metrics import accuracy, f1_score, ndcg, pairwise_accuracy, sub_em
from verifiers.clients import resolve_client
from verifiers.clients.openai_chat_completions_client import OpenAIChatCompletionsClient
from verifiers.rubrics.judge_rubric import JudgeRubric
from verifiers.types import ClientConfig, Messages, UserMessage
from verifiers.utils.message_utils import maybe_normalize_messages


class _LbpJudge(JudgeRubric):
    """Catch ``RuntimeError`` from ``JudgeRubric.judge`` (API failures) → synthetic ``NO`` for retry."""

    async def judge(self, prompt, completion, answer, state=None):
        try:
            return await super().judge(prompt, completion, answer, state)
        except RuntimeError as e:
            return f"NO\nJudge call failed ({e}). Revise and retry when available."


# =============================================================================
# Environment tips
# =============================================================================

_ENV_TIPS = """
<env_tips>
Read the long context carefully. For retrieval-style tasks, note document structure (sections, lists, numbering) \
before deep reading. Follow the answer format required by the question (e.g. [Answer] / [答案] markers when specified).
</env_tips>"""

IN_LOOP_JUDGE_INSTRUCTION_SUFFIX = """\n\nEach time you respond with an answer, an automatic judge compares it to \
the reference. If it is judged incorrect, you will receive concise feedback as the next user message. Revise and \
respond again until the judge accepts your answer or you run out of turns."""

_EXCLUDED_TASK_PREFIXES = ("T4.",)

_PRIME_INFERENCE_API_BASE = "https://api.pinference.ai/api/v1"
# Prime Inference uses provider-prefixed model ids; bare OpenAI-style names return 404.
_DEFAULT_PRIME_JUDGE_MODEL = "openai/gpt-4.1-mini"


_TASK_METRIC_MAP: dict[str, str] = {
    "T1.1": "ndcg",
    "T1.2": "ndcg",
    "T2.1": "pairwise_accuracy",
    "T2.2": "pairwise_accuracy",
    "T3.1": "accuracy",
    "T3.2": "accuracy",
    "T5.1": "f1_score",
    "T5.2": "f1_score",
    "T6.1": "sub_em",
    "T6.2": "f1_score",
    "T6.3": "pairwise_accuracy",
    "T7.1": "f1_score",
    "T7.2": "f1_score",
    "T7.3": "f1_score",
    "T8.1": "sub_em",
    "T8.2": "sub_em",
    "T8.3": "sub_em",
    "T9.1": "f1_score",
    "T9.2": "f1_score",
    "T10.1": "sub_em",
    "T10.2": "sub_em",
    "T11.1": "accuracy",
    "T11.2": "accuracy",
}

_METRIC_FUNCTIONS = {
    "accuracy": accuracy,
    "f1_score": f1_score,
    "sub_em": sub_em,
    "ndcg": ndcg,
    "pairwise_accuracy": pairwise_accuracy,
}


def _compute_task_metric(secondary_task: str, answers: list[str], prediction: str) -> float:
    prefix = secondary_task.split(" ")[0] if " " in secondary_task else secondary_task
    metric_name = _TASK_METRIC_MAP.get(prefix, "accuracy")
    metric_fn = _METRIC_FUNCTIONS[metric_name]
    score = metric_fn(answers, prediction)
    return max(0.0, min(1.0, score))


def _lbp_judge_verdict(judge_text: str) -> tuple[bool, str]:
    raw = (judge_text or "").strip()
    if not raw:
        return False, ""
    lines = raw.splitlines()
    first_line = lines[0].strip()
    upper_line = first_line.upper()
    tokens = first_line.split()
    first_tok = tokens[0].upper() if tokens else ""

    if first_tok == "NO" or upper_line.startswith("NO"):
        correct = False
    elif first_tok == "YES" or upper_line.startswith("YES"):
        correct = True
    else:
        correct = False

    feedback = "\n".join(lines[1:]).strip()
    if not correct and not feedback:
        feedback = "The judge did not find the submission correct; revise using the question and the long context."
    return correct, feedback


def _format_user_prompt(
    question_stem: str,
    raw_context: str,
    *,
    prompt_in_context_file: bool,
) -> str:
    """Inline full context in the user message (no context file). If ``prompt_in_context_file``, use a JSON object with ``query`` and ``context`` keys."""
    if prompt_in_context_file:
        payload = json.dumps({"query": question_stem, "context": raw_context}, ensure_ascii=False)
        return (
            'The task query and long context are below as one JSON object (keys "query" and "context"). '
            "Answer following the instructions in the query.\n\n"
            f"{payload}"
        )
    return f"{question_stem}\n\n## Long Context\n\n{raw_context}"


def _assistant_plain_text_from_messages(completion: vf.Messages) -> str:
    """Best-effort assistant text for Phase 2 tag parsing (handles string or parts)."""
    chunks: list[str] = []
    for msg in completion or []:
        if isinstance(msg, dict):
            role = msg.get("role")
            content = msg.get("content", "")
        else:
            role = getattr(msg, "role", None)
            content = getattr(msg, "content", "")
        if role != "assistant":
            continue
        if isinstance(content, str):
            chunks.append(content)
        elif isinstance(content, list):
            for p in content:
                if isinstance(p, dict) and p.get("type") == "text":
                    chunks.append(str(p.get("text", "")))
        else:
            chunks.append(str(content or ""))
    return "\n".join(chunks).strip()


class LongBenchProInLoopJudgeEnv(vf.MultiTurnEnv):
    """In-loop LLM judge: runs after each assistant message and returns feedback (``MultiTurnEnv``)."""

    def __init__(self, *, judge_rubric: JudgeRubric, **kwargs: Any):
        self._lbp_judge_rubric = judge_rubric
        super().__init__(**kwargs)

    async def env_response(self, _messages: vf.Messages, state: vf.State, **_kwargs: Any) -> vf.Messages:
        last_completion = state["trajectory"][-1]["completion"]
        text = self._lbp_judge_rubric.parser.parse_answer(last_completion) or ""
        state["final_answer"] = text

        answers = json.loads(state.get("answer", "[]"))
        ground_truth = "; ".join(answers)
        judge_text = await self._lbp_judge_rubric.judge(
            state["prompt"],
            last_completion,
            ground_truth,
            state,
        )
        correct, feedback = _lbp_judge_verdict(judge_text)

        if correct:
            done = UserMessage(content="The judge accepted your answer. Task complete.")
            state["final_env_response"] = [done]
            return [done]

        follow_up = UserMessage(
            content=(
                "Judge feedback (your previous answer was not accepted):\n\n"
                f"{feedback}\n\n"
                "Revise and respond with a corrected answer."
            ),
        )
        return [follow_up]


class LongBenchProPhase2SkillReinjectEnv(LongBenchProInLoopJudgeEnv):
    """Phase 2 weak baseline: reinject ``<phase2_skill>`` from the prior assistant turn as a leading system message."""

    def __init__(self, *, phase2_skill_max_chars: int = 6000, **kwargs: Any):
        self._phase2_skill_max_chars = int(phase2_skill_max_chars)
        super().__init__(**kwargs)

    async def get_prompt_messages(self, state: vf.State) -> Messages:
        base = await super().get_prompt_messages(state)
        if len(state["trajectory"]) == 0:
            return base
        prev_completion = state["trajectory"][-1].get("completion") or []
        text = _assistant_plain_text_from_messages(prev_completion)
        skill = extract_phase2_skill_block(text)
        if not skill:
            return base
        if len(skill) > self._phase2_skill_max_chars:
            skill = skill[: self._phase2_skill_max_chars] + "\n... (truncated)"
        sys_msg: dict[str, str] = {
            "role": "system",
            "content": (
                "<phase2_skill_carryover>\n"
                "Reinjected from your previous assistant message's <phase2_skill> block only. "
                "Not judge feedback; not ground truth.\n\n"
                f"{skill}\n"
                "</phase2_skill_carryover>"
            ),
        }
        merged = [sys_msg, *base]
        return maybe_normalize_messages(merged, field_name="prompt_messages_phase2_reinject")


def load_environment(
    split: str = "test",
    shuffle: bool = False,
    seed: int | None = None,
    thinking: bool = False,
    include_env_tips: bool = False,
    prompt_in_context_file: bool = False,
    language: Literal["all", "English", "Chinese"] = "English",
    token_length: Literal["all", "8k", "16k", "32k", "64k", "128k", "256k"] = "all",
    difficulty: Literal["all", "Easy", "Moderate", "Hard", "Extreme"] = "all",
    primary_task: str | None = None,
    secondary_task: str | None = None,
    dataset_start_index: int = 0,
    phase1_slice: bool = False,
    phase1_working_memory: Phase1MemoryMode = "off",
    phase2_skill_mode: Phase2SkillMode = "off",
    phase2_skill_max_chars: int = 6000,
    judge_model: str = _DEFAULT_PRIME_JUDGE_MODEL,
    judge_api_key_var: str = "PRIME_API_KEY",
    judge_base_url: str | None = None,
    judge_sampling_args: dict[str, Any] | None = None,
    judge_feedback_mode: JudgeFeedbackMode = "total_score",
    in_loop_judge: bool = True,
    max_turns: int = 8,
    **kwargs: Any,
) -> vf.Environment:
    """
    Load LongBench-Pro with context and question in the user message.

    ``prompt_in_context_file`` selects either a single JSON object (``query`` and ``context``)
    or the query stem plus a ``## Long Context`` section.

    Args:
        split: Dataset split (LongBench-Pro only has ``\"test\"``).
        shuffle: Whether to shuffle the dataset.
        seed: Random seed for shuffling.
        thinking: If True, use ``question_thinking``; otherwise ``question_nonthinking``.
        include_env_tips: Append optional reading-strategy tips to the query stem.
        prompt_in_context_file: If True, one JSON object with ``query`` and ``context``; \
            if False, query stem plus a markdown long-context section.
        language: ``\"English\"``, ``\"Chinese\"``, or ``\"all\"``.
        token_length: Filter by advertised context length bucket or ``\"all\"``.
        difficulty: Filter by difficulty or ``\"all\"``.
        primary_task: Optional primary task filter.
        secondary_task: Optional secondary task filter.
        dataset_start_index: Skip the first N rows after filters and transform.
        phase1_slice: If True, pin a fixed “hard” slice when filters are still broad: T6.1 clustering @ 32k context \
            (override by passing ``secondary_task`` / ``token_length`` explicitly).
        phase1_working_memory: Phase 1 scaffolding — checklist, hypothesis log, “what failed last time”. \
            ``chat`` keeps notes in assistant messages only; ``repl_files`` is invalid here (no REPL).
        phase2_skill_mode: Phase 2 chat harness. ``chat_no_file`` = iterative judge feedback without a skill file; \
            ``chat_system_reinject`` = reinject prior ``<phase2_skill>`` block as a system message; ``off`` disables. \
            ``rlm_skill_file`` is invalid on chat env.
        phase2_skill_max_chars: Soft cap for reinjected skill text (truncated if longer).
        judge_model: Judge model id on Prime Inference (e.g. ``openai/gpt-4.1-mini`` or ``z-ai/glm-4.7``).
        judge_api_key_var: Env var for the judge API key.
        judge_base_url: API base URL; default Prime Inference.
        judge_sampling_args: Optional sampling args for the judge.
        judge_feedback_mode: ``total_score`` (default): four 0/1 criterion lines plus ``TOTAL: x/4``; \
            ``single_criterion``: one ``VIOLATED: …`` line plus one feedback sentence (sparse signal). \
            Templates live in ``longbenchpro_prompts``.
        in_loop_judge: If True, run the LLM judge **during** the rollout after each assistant message \
            (``max_turns`` cap) and surface feedback in chat. If False, single-turn rollout; the judge runs only \
            via the rubric at trajectory end.
        max_turns: Max assistant messages when ``in_loop_judge`` is True.
        **kwargs: Forwarded to ``SingleTurnEnv`` / ``MultiTurnEnv``.
    """
    if phase1_working_memory == "repl_files":
        raise ValueError("longbenchpro has no REPL; use phase1_working_memory='chat' or 'off'.")
    if phase2_skill_mode not in ("off", "chat_no_file", "chat_system_reinject"):
        raise ValueError(
            f"longbenchpro: phase2_skill_mode must be 'off', 'chat_no_file', or 'chat_system_reinject'; "
            f"got {phase2_skill_mode!r}"
        )

    effective_secondary_task, effective_token_length = resolve_phase1_lbp_filters(
        phase1_slice=phase1_slice,
        secondary_task=secondary_task,
        token_length=token_length,
    )
    phase1_suffix = phase1_working_memory_suffix(phase1_working_memory, rlm=False)
    phase2_suffix = phase2_skill_suffix(
        phase2_skill_mode,
        rlm=False,
        max_chars=int(phase2_skill_max_chars),
    )

    question_column = "question_thinking" if thinking else "question_nonthinking"

    def transform_example(example: dict[str, Any], idx: int) -> dict[str, Any]:
        question = example[question_column]
        raw_context = example["context"]
        answers = example["answer"]
        sec_task = example["secondary_task"]

        question_stem = question
        if include_env_tips:
            question_stem = question_stem + _ENV_TIPS
        if in_loop_judge:
            question_stem = question_stem + IN_LOOP_JUDGE_INSTRUCTION_SUFFIX
        if phase1_suffix:
            question_stem = question_stem + phase1_suffix
        if phase2_suffix:
            question_stem = question_stem + phase2_suffix

        user_content = _format_user_prompt(question_stem, raw_context, prompt_in_context_file=prompt_in_context_file)

        return {
            "example_id": idx,
            "prompt": [{"role": "user", "content": user_content}],
            "task": "longbenchpro",
            "answer": json.dumps(answers),
            "info": {
                "context": raw_context,
                "raw_question": question,
                "secondary_task": sec_task,
                "primary_task": example["primary_task"],
                "difficulty": example["difficulty"],
                "language": example["language"],
                "token_length": example["token_length"],
                "dataset_example_id": example["id"],
                "prompt_in_context_file": prompt_in_context_file,
                "phase1_slice": phase1_slice,
                "phase1_working_memory": phase1_working_memory,
                "phase2_skill_mode": phase2_skill_mode,
                "phase2_skill_max_chars": int(phase2_skill_max_chars),
            },
        }

    def build_dataset():
        raw_dataset = load_dataset("caskcsg/LongBench-Pro", split=split)

        raw_dataset = raw_dataset.filter(
            lambda x: not any(x["secondary_task"].startswith(p) for p in _EXCLUDED_TASK_PREFIXES)
        )

        if language != "all":
            raw_dataset = raw_dataset.filter(lambda x: x["language"] == language)
        if effective_token_length != "all":
            raw_dataset = raw_dataset.filter(lambda x: x["token_length"] == effective_token_length)
        if difficulty != "all":
            raw_dataset = raw_dataset.filter(lambda x: x["difficulty"] == difficulty)
        if primary_task is not None:
            raw_dataset = raw_dataset.filter(lambda x: x["primary_task"] == primary_task)
        if effective_secondary_task is not None:
            raw_dataset = raw_dataset.filter(lambda x: x["secondary_task"] == effective_secondary_task)

        dataset = raw_dataset.map(
            transform_example,
            with_indices=True,
            remove_columns=raw_dataset.column_names,
            writer_batch_size=100,
        )

        if dataset_start_index > 0:
            n_total = len(dataset)
            if dataset_start_index >= n_total:
                raise ValueError(f"dataset_start_index={dataset_start_index} out of range for dataset size {n_total}")
            dataset = dataset.select(range(dataset_start_index, n_total))

        if shuffle:
            _seed = seed if seed is not None else random.randint(1000, 100_000_000)
            dataset = dataset.shuffle(seed=_seed)

        return dataset

    judge_client_config = ClientConfig(
        client_type="openai_chat_completions",
        api_key_var=judge_api_key_var,
        api_base_url=judge_base_url if judge_base_url is not None else _PRIME_INFERENCE_API_BASE,
        timeout=1200.0,
    )
    judge_wrapped = resolve_client(judge_client_config)
    if not isinstance(judge_wrapped, OpenAIChatCompletionsClient):
        raise TypeError(
            f"longbenchpro judge requires client_type 'openai_chat_completions'; got {type(judge_wrapped).__name__}"
        )
    judge_async_client = judge_wrapped.client

    judge_rubric = _LbpJudge(
        judge_client=judge_async_client,
        judge_model=judge_model,
        judge_prompt=lbp_judge_prompt_for_mode(judge_feedback_mode),
        judge_sampling_args=judge_sampling_args,
    )

    def _parsed_answer_for_metrics(state: vf.State) -> str:
        rubric_parser = judge_rubric.parser
        comp = state.get("completion")
        if comp:
            return rubric_parser.parse_answer(comp) or ""
        return state.get("final_answer", "") or ""

    async def judge_reward(state: vf.State, judge, **_kwargs: Any) -> float:
        answers = json.loads(state.get("answer", "[]"))
        ground_truth = "; ".join(answers)
        completion = state.get("completion") or [{"role": "assistant", "content": state.get("final_answer", "") or ""}]
        judge_response = await judge(
            state["prompt"],
            completion,
            ground_truth,
            state,
        )
        correct, _ = _lbp_judge_verdict(judge_response)
        return 1.0 if correct else 0.0

    def task_metric_reward(state: vf.State, **_kwargs: Any) -> float:
        response = _parsed_answer_for_metrics(state)
        answers = json.loads(state.get("answer", "[]"))
        sec_task = state["info"]["secondary_task"]
        return _compute_task_metric(sec_task, answers, response)

    def contains_answer_reward(state: vf.State, **_kwargs: Any) -> float:
        response = _parsed_answer_for_metrics(state).strip().lower()
        answers = json.loads(state.get("answer", "[]"))
        return 1.0 if any(a.strip().lower() in response for a in answers) else 0.0

    judge_rubric.add_reward_func(judge_reward, weight=1.0)
    judge_rubric.add_reward_func(task_metric_reward, weight=0.0)
    judge_rubric.add_reward_func(contains_answer_reward, weight=0.0)

    if not in_loop_judge:
        return vf.SingleTurnEnv(
            dataset=build_dataset,
            eval_dataset=build_dataset,
            rubric=judge_rubric,
            **kwargs,
        )

    env_cls: type[LongBenchProInLoopJudgeEnv] = (
        LongBenchProPhase2SkillReinjectEnv
        if phase2_skill_mode == "chat_system_reinject"
        else LongBenchProInLoopJudgeEnv
    )
    reinject_kw: dict[str, Any] = {}
    if env_cls is LongBenchProPhase2SkillReinjectEnv:
        reinject_kw["phase2_skill_max_chars"] = int(phase2_skill_max_chars)

    return env_cls(
        judge_rubric=judge_rubric,
        dataset=build_dataset,
        eval_dataset=build_dataset,
        rubric=judge_rubric,
        max_turns=max_turns,
        **reinject_kw,
        **kwargs,
    )
