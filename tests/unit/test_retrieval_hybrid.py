"""Unit tests for BM25, MMR, and hybrid retrieval."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.retrieval.base import RetrievalResult
from backend.retrieval.bm25 import BM25Scorer
from backend.retrieval.hybrid import HybridRetrievalConfig, HybridRetrievalService, _min_max_norm
from backend.retrieval.mmr import mmr_rerank
from backend.vector_store.base import SearchResult


# ---------------------------------------------------------------------------
# BM25Scorer
# ---------------------------------------------------------------------------


def test_bm25_scores_relevant_doc_higher():
    scorer = BM25Scorer().fit(["python programming language", "cooking recipes food"])
    scores = scorer.score("python")
    assert scores[0] > scores[1]


def test_bm25_zero_scores_for_unknown_query():
    scorer = BM25Scorer().fit(["hello world"])
    scores = scorer.score("zzz_nonexistent")
    assert scores[0] == 0.0


def test_bm25_empty_corpus_returns_empty():
    scorer = BM25Scorer().fit([])
    assert scorer.score("anything") == []


def test_bm25_multiple_docs():
    docs = [
        "machine learning algorithms",
        "deep learning neural networks",
        "cooking pasta recipes",
    ]
    scorer = BM25Scorer().fit(docs)
    scores = scorer.score("learning")
    # Both ML docs should score higher than cooking
    assert scores[0] > scores[2]
    assert scores[1] > scores[2]


# ---------------------------------------------------------------------------
# MMR re-ranker
# ---------------------------------------------------------------------------


def _result(chunk_id: str, score: float) -> RetrievalResult:
    return RetrievalResult(
        chunk_id=chunk_id, document_id="d", workspace_id="w",
        text=chunk_id, score=score
    )


def test_mmr_empty_input():
    assert mmr_rerank([], []) == []


def test_mmr_raises_on_length_mismatch():
    with pytest.raises(ValueError):
        mmr_rerank([_result("a", 0.9)], [[0.1], [0.2]])


def test_mmr_pure_relevance_preserves_order():
    results = [_result("a", 0.9), _result("b", 0.7), _result("c", 0.5)]
    embs = [[1.0], [0.5], [0.0]]
    reranked = mmr_rerank(results, embs, lambda_=1.0, top_k=3)
    assert [r.chunk_id for r in reranked] == ["a", "b", "c"]


def test_mmr_diversifies_when_lambda_zero():
    # All identical embeddings — with lambda=0 (pure diversity) subsequent
    # picks should still proceed without error.
    results = [_result("a", 0.9), _result("b", 0.8), _result("c", 0.7)]
    embs = [[1.0, 0.0], [1.0, 0.0], [0.0, 1.0]]
    reranked = mmr_rerank(results, embs, lambda_=0.0, top_k=3)
    assert len(reranked) == 3


def test_mmr_top_k_limits_output():
    results = [_result(str(i), 1.0 - i * 0.1) for i in range(5)]
    embs = [[float(i)] for i in range(5)]
    reranked = mmr_rerank(results, embs, top_k=2)
    assert len(reranked) == 2


# ---------------------------------------------------------------------------
# _min_max_norm helper
# ---------------------------------------------------------------------------


def test_min_max_norm_standard():
    normed = _min_max_norm([0.0, 0.5, 1.0])
    assert normed == [0.0, 0.5, 1.0]


def test_min_max_norm_flat():
    normed = _min_max_norm([0.5, 0.5, 0.5])
    assert normed == [0.0, 0.0, 0.0]


# ---------------------------------------------------------------------------
# HybridRetrievalService
# ---------------------------------------------------------------------------


def _make_store_with_hits(*hits) -> MagicMock:
    store = MagicMock()
    store.search = AsyncMock(return_value=list(hits))
    return store


def _hit(id_: str, score: float, text: str = "") -> SearchResult:
    return SearchResult(
        id=id_, score=score,
        metadata={"document_id": "d", "workspace_id": "w", "text": text, "chunk_index": 0},
    )


@pytest.mark.asyncio
async def test_hybrid_returns_fused_results():
    store = _make_store_with_hits(
        _hit("c1", 0.9, "python machine learning"),
        _hit("c2", 0.7, "cooking pasta"),
    )
    svc = HybridRetrievalService(vector_store=store)
    cfg = HybridRetrievalConfig(index_id=uuid.uuid4(), top_k=2)
    results = await svc.retrieve([0.1, 0.2], "python", cfg)
    assert len(results) == 2


@pytest.mark.asyncio
async def test_hybrid_empty_candidates_returns_empty():
    store = _make_store_with_hits()
    svc = HybridRetrievalService(vector_store=store)
    cfg = HybridRetrievalConfig(index_id=uuid.uuid4(), top_k=5)
    results = await svc.retrieve([0.0], "query", cfg)
    assert results == []


@pytest.mark.asyncio
async def test_hybrid_respects_top_k():
    hits = [_hit(f"c{i}", 0.9 - i * 0.05, f"doc {i}") for i in range(10)]
    store = _make_store_with_hits(*hits)
    svc = HybridRetrievalService(vector_store=store)
    cfg = HybridRetrievalConfig(index_id=uuid.uuid4(), top_k=3)
    results = await svc.retrieve([0.1], "doc", cfg)
    assert len(results) <= 3


@pytest.mark.asyncio
async def test_hybrid_with_mmr_enabled():
    hits = [_hit(f"c{i}", 0.9 - i * 0.1, f"text {i}") for i in range(4)]
    store = _make_store_with_hits(*hits)
    svc = HybridRetrievalService(vector_store=store)
    cfg = HybridRetrievalConfig(index_id=uuid.uuid4(), top_k=3, use_mmr=True, mmr_lambda=0.7)
    results = await svc.retrieve([0.1], "text", cfg)
    assert 1 <= len(results) <= 3


@pytest.mark.asyncio
async def test_hybrid_alpha_weights_vector_heavily():
    # With alpha=1.0 only vector score matters — result order matches vector score
    store = _make_store_with_hits(
        _hit("high", 0.95, "unrelated text zzz"),
        _hit("low", 0.30, "unrelated text zzz"),
    )
    svc = HybridRetrievalService(vector_store=store)
    cfg = HybridRetrievalConfig(index_id=uuid.uuid4(), top_k=2, alpha=1.0)
    results = await svc.retrieve([0.1], "query", cfg)
    assert results[0].chunk_id == "high"
