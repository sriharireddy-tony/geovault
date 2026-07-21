"""Lightweight RAG evaluation metrics (faithfulness heuristics + LangSmith-ready scores)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EvalScores:
    groundedness: float
    citation_coverage: float
    has_context: bool
    notes: list[str] = field(default_factory=list)


def evaluate_answer(*, question: str, answer: str, contexts: list[str], citation_count: int) -> EvalScores:
    notes: list[str] = []
    has_context = bool(contexts)
    if not has_context:
        grounded = 1.0 if "enough information" in answer.lower() or "do not have" in answer.lower() else 0.2
        notes.append("no_retrieval_context")
        return EvalScores(groundedness=grounded, citation_coverage=0.0, has_context=False, notes=notes)

    # Token overlap heuristic between answer and concatenated context
    ctx = " ".join(contexts).lower()
    ans_tokens = {t for t in _tokens(answer) if len(t) > 3}
    ctx_tokens = set(_tokens(ctx))
    if not ans_tokens:
        overlap = 0.0
    else:
        overlap = len(ans_tokens & ctx_tokens) / max(1, len(ans_tokens))

    cite_score = min(1.0, citation_count / 3.0) if citation_count else 0.0
    if "[" in answer and "]" in answer:
        cite_score = max(cite_score, 0.5)
        notes.append("inline_citation_markers")

    return EvalScores(
        groundedness=round(overlap, 3),
        citation_coverage=round(cite_score, 3),
        has_context=True,
        notes=notes,
    )


def _tokens(text: str) -> list[str]:
    return [t.strip(".,;:!?()[]{}\"'").lower() for t in text.split()]
