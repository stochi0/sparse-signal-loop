from typing import Any


def judge_reference_from_row(x: dict[str, Any]) -> str:
    """Build hidden reference text for the LLM judge (patch + problem when available)."""
    ps = (x.get("problem_statement") or "").strip()
    patch = (x.get("patch") or "").strip()
    if len(patch) > 12_000:
        patch = patch[:12_000] + "\n... (truncated)"
    if patch:
        return (
            "Reference fix patch (for grading only; do not disclose in feedback to the agent):\n"
            f"```diff\n{patch}\n```\n\nProblem statement:\n{ps[:8000]}"
        )
    return (
        "Problem statement (no reference patch in dataset; judge whether the submission plausibly addresses it):\n"
        f"{ps[:12_000]}"
    )


def msap_judge_verdict(judge_text: str) -> tuple[bool, str]:
    """Parse YES/NO first line; remainder is feedback (same convention as longbenchpro)."""
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
        feedback = (
            "The judge did not accept this submission; keep iterating on a fix consistent with the PR description."
        )
    return correct, feedback
