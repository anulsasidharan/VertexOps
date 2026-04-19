"""Maximum Marginal Relevance (MMR) re-ranker for result diversification."""

import math

from backend.retrieval.base import RetrievalResult


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


def mmr_rerank(
    results: list[RetrievalResult],
    embeddings: list[list[float]],
    lambda_: float = 0.5,
    top_k: int | None = None,
) -> list[RetrievalResult]:
    """Re-rank *results* using MMR to balance relevance and diversity.

    Args:
        results: Ordered retrieval results (highest score first).
        embeddings: Per-result embedding vectors (same length as results).
        lambda_: Trade-off weight; 1.0 = pure relevance, 0.0 = pure diversity.
        top_k: Maximum results to return; defaults to len(results).

    Returns:
        Re-ranked list of at most top_k results.
    """
    if not results:
        return []
    if len(results) != len(embeddings):
        raise ValueError("results and embeddings must have the same length")

    k = top_k if top_k is not None else len(results)
    k = min(k, len(results))

    remaining = list(range(len(results)))
    selected: list[int] = []

    # Relevance scores normalised to [0, 1] for the MMR formula
    max_score = max(r.score for r in results) or 1.0
    rel = [r.score / max_score for r in results]

    while len(selected) < k and remaining:
        best_idx = -1
        best_val = float("-inf")
        for i in remaining:
            redundancy = (
                max(_cosine(embeddings[i], embeddings[s]) for s in selected) if selected else 0.0
            )
            val = lambda_ * rel[i] - (1 - lambda_) * redundancy
            if val > best_val:
                best_val = val
                best_idx = i
        selected.append(best_idx)
        remaining.remove(best_idx)

    return [results[i] for i in selected]
