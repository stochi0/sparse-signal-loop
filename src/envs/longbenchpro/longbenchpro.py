"""
LongBench-Pro long-context environment (non-RLM).

Same dataset, judge, and task metrics as ``longbenchpro_rlm``, but the model receives
the full task in chat messages (no REPL / sandbox). Optional multi-turn loop: an LLM
judge runs after every assistant turn (``verifiers.MultiTurnEnv``).

Dataset: caskcsg/LongBench-Pro
Reference: https://github.com/caskcsg/longcontext/tree/main/LongBench-Pro
"""

from __future__ import annotations

import json
import random
import re
from itertools import combinations
from typing import Any, Literal

import verifiers as vf
from datasets import load_dataset
from longbenchpro_prompts import JudgeFeedbackMode, lbp_judge_prompt_for_mode
from verifiers.clients import resolve_client
from verifiers.clients.openai_chat_completions_client import OpenAIChatCompletionsClient
from verifiers.rubrics.judge_rubric import JudgeRubric
from verifiers.types import ClientConfig, UserMessage

# =============================================================================
# Environment tips (no REPL — avoid RLM-only workflow hints)
# =============================================================================

_ENV_TIPS = """
<env_tips>
Read the long context carefully. For retrieval-style tasks, note document structure (sections, lists, numbering) \
before deep reading. Follow the answer format required by the question (e.g. [Answer] / [答案] markers when specified).
</env_tips>"""

ITERATIVE_JUDGE_INSTRUCTION_SUFFIX = """\n\nEach time you respond with an answer, an automatic judge compares it to \
the reference. If it is judged incorrect, you will receive concise feedback as the next user message. Revise and \
respond again until the judge accepts your answer or you run out of turns."""

_EXCLUDED_TASK_PREFIXES = ("T4.",)

_PRIME_INFERENCE_API_BASE = "https://api.pinference.ai/api/v1"
# Prime Inference uses provider-prefixed model ids; bare OpenAI-style names return 404.
_DEFAULT_PRIME_JUDGE_MODEL = "openai/gpt-4.1-mini"


# =============================================================================
# Task-specific metrics (same as LongBench-Pro / longbenchpro_rlm)
# =============================================================================


def _fix_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _normalize_prediction(prediction: str) -> list[str]:
    if "[Answer]" in prediction:
        prediction = prediction[prediction.rfind("[Answer]") + len("[Answer]") :]
    elif "[答案]" in prediction:
        prediction = prediction[prediction.rfind("[答案]") + len("[答案]") :]

    prediction = prediction.lower()
    lines = [_fix_spaces(line.strip()) for line in prediction.split("\n")]
    return lines


def _normalize_answers(answers: list[str]) -> list[str]:
    return [_fix_spaces(a.lower().strip()) for a in answers]


def _accuracy(answers: list[str], prediction: str) -> float:
    norm_answers = _normalize_answers(answers)
    norm_pred = _normalize_prediction(prediction)
    if not norm_answers or not norm_pred:
        return 0.0
    return 1.0 if norm_answers[0] == norm_pred[0] else 0.0


def _f1_score(answers: list[str], prediction: str) -> float:
    norm_answers = _normalize_answers(answers)
    norm_pred = _normalize_prediction(prediction)

    answer_set = set(norm_answers)
    prediction_set = set(norm_pred)

    common = answer_set & prediction_set
    if not common or not prediction_set or not answer_set:
        return 0.0

    precision = len(common) / len(prediction_set)
    recall = len(common) / len(answer_set)

    if precision + recall == 0:
        return 0.0

    return (2 * precision * recall) / (precision + recall)


def _sub_em(answers: list[str], prediction: str) -> float:
    norm_answers = _normalize_answers(answers)
    norm_pred = _normalize_prediction(prediction)

    if not norm_answers or not norm_pred:
        return 0.0

    found = sum(1.0 for a in norm_answers if a in norm_pred)
    return found / len(norm_answers)


def _ndcg(answers: list[str], prediction: str) -> float:
    try:
        import pytrec_eval
    except ImportError:
        raise ImportError("pytrec_eval is required for NDCG. Install with: pip install pytrec-eval-terrier")

    norm_answers = _normalize_answers(answers)
    norm_pred = _normalize_prediction(prediction)

    k = len(norm_answers)
    if k == 0 or not norm_pred:
        return 0.0

    qrel = {"query": {a: len(norm_answers) - i for i, a in enumerate(norm_answers)}}
    run = {"query": {p: len(norm_pred) - i for i, p in enumerate(norm_pred)}}

    ndcg_string = f"ndcg_cut.{k}"
    evaluator = pytrec_eval.RelevanceEvaluator(qrel, {ndcg_string})
    scores = evaluator.evaluate(run)

    ndcg = sum(s[f"ndcg_cut_{k}"] for s in scores.values()) / len(scores)
    return ndcg


def _pairwise_accuracy(answers: list[str], prediction: str) -> float:
    norm_answers = _normalize_answers(answers)
    norm_pred = _normalize_prediction(prediction)

    if len(norm_answers) < 2 or len(norm_pred) < 2:
        return 0.0

    n_total = len(norm_pred) * (len(norm_pred) - 1) // 2
    pred_indices = {p: i for i, p in enumerate(norm_pred)}
    n_correct = 0

    for a, b in combinations(norm_answers, 2):
        if a in pred_indices and b in pred_indices:
            if pred_indices[a] < pred_indices[b]:
                n_correct += 1

    return n_correct / n_total


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
    "accuracy": _accuracy,
    "f1_score": _f1_score,
    "sub_em": _sub_em,
    "ndcg": _ndcg,
    "pairwise_accuracy": _pairwise_accuracy,
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
        correct = "yes" in first_line.lower()

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
    """Inline full context in chat (no sandbox file). ``prompt_in_context_file`` mirrors RLM JSON shape."""
    if prompt_in_context_file:
        payload = json.dumps({"query": question_stem, "context": raw_context}, ensure_ascii=False)
        return (
            'The task query and long context are below as one JSON object (keys "query" and "context"). '
            "Answer following the instructions in the query.\n\n"
            f"{payload}"
        )
    return f"{question_stem}\n\n## Long Context\n\n{raw_context}"


class LongBenchProIterativeJudgeEnv(vf.MultiTurnEnv):
    """LLM judge after every assistant turn (``MultiTurnEnv`` chat pattern)."""

    def __init__(self, *, judge_rubric: JudgeRubric, **kwargs: Any):
        self._lbp_judge_rubric = judge_rubric
        super().__init__(**kwargs)

    async def env_response(self, messages: vf.Messages, state: vf.State, **kwargs: Any) -> vf.Messages:
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
    judge_model: str = _DEFAULT_PRIME_JUDGE_MODEL,
    judge_api_key_var: str = "PRIME_API_KEY",
    judge_base_url: str | None = None,
    judge_sampling_args: dict[str, Any] | None = None,
    judge_feedback_mode: JudgeFeedbackMode = "freeform",
    iterative_judge: bool = True,
    max_turns: int = 8,
    **kwargs: Any,
) -> vf.Environment:
    """
    Load LongBench-Pro as a standard chat environment (no RLM).

    Context is always included in the user message. ``prompt_in_context_file`` controls
    whether that content uses the same JSON layout as the RLM ``context.txt`` payload
    (inline JSON) versus question plus a ``## Long Context`` section.

    Args:
        split: Dataset split (LongBench-Pro only has ``\"test\"``).
        shuffle: Whether to shuffle the dataset.
        seed: Random seed for shuffling.
        thinking: If True, use ``question_thinking``; otherwise ``question_nonthinking``.
        include_env_tips: Append non-RLM strategy tips to the query stem.
        prompt_in_context_file: If True, one JSON object with ``query`` and ``context``; \
            if False, query stem plus a markdown long-context section.
        language: ``\"English\"``, ``\"Chinese\"``, or ``\"all\"``.
        token_length: Filter by advertised context length bucket or ``\"all\"``.
        difficulty: Filter by difficulty or ``\"all\"``.
        primary_task: Optional primary task filter.
        secondary_task: Optional secondary task filter.
        dataset_start_index: Skip the first N rows after filters and transform (same semantics as \
            ``mini_swe_agent_plus`` / ``mini_swe_agent_plus_rlm``). Use ``shuffle: false`` and the same \
            index in chat and RLM for paired evals.
        judge_model: Judge model id on Prime Inference (e.g. ``openai/gpt-4.1-mini`` or ``z-ai/glm-4.7``).
        judge_api_key_var: Env var for the judge API key.
        judge_base_url: API base URL; default Prime Inference.
        judge_sampling_args: Optional sampling args for the judge.
        judge_feedback_mode: ``freeform`` (default): concise multi-line feedback after NO; ``total_score``: \
            four 0/1 criterion lines plus ``TOTAL: x/4``; ``single_criterion``: one ``VIOLATED: …`` line plus \
            one feedback sentence (sparse signal). Prompts live in ``longbenchpro_prompts``; keep in sync with \
            ``longbenchpro_rlm_prompts`` in the RLM package.
        iterative_judge: If True, judge after each assistant message (``max_turns`` cap). \
            If False, single-turn rollout; judge only via rubric at the end.
        max_turns: Max assistant messages when ``iterative_judge`` is True. For parity with ``longbenchpro_rlm``, \
            align with ``max_judge_submissions`` (graded incorrect attempts).
        **kwargs: Forwarded to ``SingleTurnEnv`` / ``MultiTurnEnv``.
    """
    question_column = "question_thinking" if thinking else "question_nonthinking"

    def transform_example(example: dict[str, Any], idx: int) -> dict[str, Any]:
        question = example[question_column]
        raw_context = example["context"]
        answers = example["answer"]
        sec_task = example["secondary_task"]

        question_stem = question
        if include_env_tips:
            question_stem = question_stem + _ENV_TIPS
        if iterative_judge:
            question_stem = question_stem + ITERATIVE_JUDGE_INSTRUCTION_SUFFIX

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
            },
        }

    def build_dataset():
        raw_dataset = load_dataset("caskcsg/LongBench-Pro", split=split)

        raw_dataset = raw_dataset.filter(
            lambda x: not any(x["secondary_task"].startswith(p) for p in _EXCLUDED_TASK_PREFIXES)
        )

        if language != "all":
            raw_dataset = raw_dataset.filter(lambda x: x["language"] == language)
        if token_length != "all":
            raw_dataset = raw_dataset.filter(lambda x: x["token_length"] == token_length)
        if difficulty != "all":
            raw_dataset = raw_dataset.filter(lambda x: x["difficulty"] == difficulty)
        if primary_task is not None:
            raw_dataset = raw_dataset.filter(lambda x: x["primary_task"] == primary_task)
        if secondary_task is not None:
            raw_dataset = raw_dataset.filter(lambda x: x["secondary_task"] == secondary_task)

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

    judge_rubric = JudgeRubric(
        judge_client=judge_async_client,
        judge_model=judge_model,
        judge_prompt=lbp_judge_prompt_for_mode(judge_feedback_mode),
        judge_sampling_args=judge_sampling_args,
    )

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
        rubric_parser = judge_rubric.parser
        comp = state.get("completion")
        if comp:
            response = rubric_parser.parse_answer(comp) or ""
        else:
            response = state.get("final_answer", "") or ""
        answers = json.loads(state.get("answer", "[]"))
        sec_task = state["info"]["secondary_task"]
        return _compute_task_metric(sec_task, answers, response)

    def contains_answer_reward(state: vf.State, **_kwargs: Any) -> float:
        rubric_parser = judge_rubric.parser
        comp = state.get("completion")
        if comp:
            response = (rubric_parser.parse_answer(comp) or "").strip().lower()
        else:
            response = (state.get("final_answer", "") or "").strip().lower()
        answers = json.loads(state.get("answer", "[]"))
        return 1.0 if any(a.strip().lower() in response for a in answers) else 0.0

    judge_rubric.add_reward_func(judge_reward, weight=1.0)
    judge_rubric.add_reward_func(task_metric_reward, weight=0.0)
    judge_rubric.add_reward_func(contains_answer_reward, weight=0.0)

    if not iterative_judge:
        return vf.SingleTurnEnv(
            dataset=build_dataset,
            eval_dataset=build_dataset,
            rubric=judge_rubric,
            **kwargs,
        )

    return LongBenchProIterativeJudgeEnv(
        judge_rubric=judge_rubric,
        dataset=build_dataset,
        eval_dataset=build_dataset,
        rubric=judge_rubric,
        max_turns=max_turns,
        **kwargs,
    )
