"""Hybrid retrieval: fuses dense vector scores with BM25 lexical scores."""

import logging
from dataclasses import dataclass
from typing import Any, Optional
from uuid import UUID

from backend.retrieval.base import RetrievalConfig, RetrievalResult
from backend.retrieval.bm25 import BM25Scorer
from backend.retrieval.service import RetrievalService
from backend.vector_store.base import BaseVectorStore

logger = logging.getLogger(__name__)


@dataclass
class HybridRetrievalConfig:
    """Extended retrieval config adding lexical and MMR options."""

    index_id: UUID
    top_k: int = 5
    min_score: float = 0.0
    namespace: Optional[str] = None
    filters: Optional[dict[str, Any]] = None
    # Hybrid
    alpha: float = 0.7  # weight for vector score (1-alpha goes to BM25)
    candidate_multiplier: int = 3  # fetch more candidates before fusion
    # MMR
    use_mmr: bool = False
    mmr_lambda: float = 0.5


def _min_max_norm(scores: list[float]) -> list[float]:
    """Normalise scores to [0, 1]; returns all-zeros if range is zero."""
    lo, hi = min(scores), max(scores)
    if hi == lo:
        return [0.0] * len(scores)
    return [(s - lo) / (hi - lo) for s in scores]


class HybridRetrievalService:
    """Combines vector similarity and BM25 lexical scoring via score fusion."""

    def __init__(
        self,
        vector_store: BaseVectorStore | None = None,
        query_text: str = "",
    ) -> None:
        self._base = RetrievalService(vector_store=vector_store)

    async def retrieve(
        self,
        query_vector: list[float],
        query_text: str,
        config: HybridRetrievalConfig,
    ) -> list[RetrievalResult]:
        """Fetch candidates, fuse vector + BM25 scores, optionally apply MMR."""
        # Fetch more candidates than needed for better fusion coverage
        base_cfg = RetrievalConfig(
            index_id=config.index_id,
            top_k=config.top_k * config.candidate_multiplier,
            min_score=0.0,
            namespace=config.namespace,
            filters=config.filters,
        )
        candidates = await self._base.retrieve(query_vector, base_cfg)

        if not candidates:
            return []

        # BM25 over candidate texts
        texts = [c.text for c in candidates]
        bm25 = BM25Scorer().fit(texts)
        lex_scores = bm25.score(query_text)

        # Normalise both score lists
        vec_scores = _min_max_norm([c.score for c in candidates])
        lex_norm = (
            _min_max_norm(lex_scores) if any(s > 0 for s in lex_scores) else [0.0] * len(lex_scores)
        )

        # Fuse
        fused: list[RetrievalResult] = []
        for i, result in enumerate(candidates):
            fused_score = config.alpha * vec_scores[i] + (1 - config.alpha) * lex_norm[i]
            if fused_score < config.min_score:
                continue
            fused.append(
                RetrievalResult(
                    chunk_id=result.chunk_id,
                    document_id=result.document_id,
                    workspace_id=result.workspace_id,
                    text=result.text,
                    score=fused_score,
                    chunk_index=result.chunk_index,
                    section_path=result.section_path,
                    metadata=result.metadata,
                )
            )

        fused.sort(key=lambda r: r.score, reverse=True)
        top = fused[: config.top_k]

        if config.use_mmr and top:
            from backend.retrieval.mmr import mmr_rerank

            # Use fused score vector as proxy embedding for MMR (lightweight)
            proxy = [[r.score] for r in top]
            top = mmr_rerank(top, proxy, lambda_=config.mmr_lambda, top_k=config.top_k)

        logger.info(
            "hybrid retrieve: index=%s candidates=%d returned=%d",
            config.index_id,
            len(candidates),
            len(top),
        )
        return top
