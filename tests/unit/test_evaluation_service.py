"""Unit tests for evaluation metrics and service."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.evaluation.datasets import build_synthetic_eval_cases_from_chunk_texts
from backend.evaluation.metrics import (
    AggregateMetrics,
    CaseMetrics,
    aggregate_case_metrics,
    compute_case_metrics,
)


# ---------------------------------------------------------------------------
# compute_case_metrics
# ---------------------------------------------------------------------------

def test_build_synthetic_eval_cases_from_chunk_texts():
    rows = build_synthetic_eval_cases_from_chunk_texts(
        ["First paragraph. Second bit.", "", "   "],
        max_cases=10,
    )
    assert len(rows) == 1
    assert "excerpt" in rows[0]["question"]
    assert rows[0]["ground_truth"]
    assert rows[0]["context"].startswith("First paragraph")


def test_compute_case_metrics_relevant_answer():
    m = compute_case_metrics(
        question="What is Python?",
        predicted="Python is a programming language.",
        ground_truth="Python is a high-level programming language.",
        context="Python programming language overview.",
        latency_ms=120.0,
        token_count=50,
    )
    assert 0.0 < m.relevance <= 1.0
    assert 0.0 < m.faithfulness <= 1.0
    assert m.latency_ms == 120.0
    assert m.token_count == 50
    assert m.failure_type is None


def test_compute_case_metrics_empty_predicted_flags_failure():
    m = compute_case_metrics(
        question="What is X?",
        predicted="",
        ground_truth="X is something.",
        context="context",
    )
    assert m.failure_type == "empty_response"
    assert m.relevance == 0.0


def test_compute_case_metrics_whitespace_only_is_empty():
    m = compute_case_metrics(question="Q?", predicted="   ", ground_truth=None, context=None)
    assert m.failure_type == "empty_response"


def test_compute_case_metrics_low_overlap_flags_failure():
    m = compute_case_metrics(
        question="What is Python?",
        predicted="xyzabc qwertyuiop zzzqqq mmmnnn",
        ground_truth="Python is a programming language.",
        context=None,
    )
    assert m.failure_type == "low_overlap"


def test_compute_case_metrics_cost_calculation():
    m = compute_case_metrics(
        question="Q?", predicted="A.", ground_truth=None, context=None,
        token_count=1000, cost_per_1k_tokens=0.002,
    )
    assert abs(m.cost_usd - 0.002) < 1e-6


def test_compute_case_metrics_no_ground_truth_no_failure():
    m = compute_case_metrics(
        question="What?", predicted="Some answer.", ground_truth=None, context=None
    )
    assert m.failure_type is None


def test_compute_case_metrics_no_context_zero_faithfulness():
    m = compute_case_metrics(
        question="Q?", predicted="some answer", ground_truth=None, context=None
    )
    assert m.faithfulness == 0.0


# ---------------------------------------------------------------------------
# aggregate_case_metrics
# ---------------------------------------------------------------------------

def test_aggregate_empty_cases():
    agg = aggregate_case_metrics([])
    assert agg.case_count == 0
    assert agg.avg_relevance == 0.0
    assert agg.failure_rate == 0.0


def test_aggregate_all_passing():
    cases = [
        CaseMetrics(relevance=0.8, faithfulness=0.7, latency_ms=100, token_count=50, cost_usd=0.001),
        CaseMetrics(relevance=0.6, faithfulness=0.5, latency_ms=200, token_count=80, cost_usd=0.002),
    ]
    agg = aggregate_case_metrics(cases)
    assert agg.case_count == 2
    assert abs(agg.avg_relevance - 0.7) < 0.001
    assert abs(agg.avg_faithfulness - 0.6) < 0.001
    assert abs(agg.avg_latency_ms - 150.0) < 0.001
    assert agg.total_tokens == 130
    assert agg.failure_count == 0
    assert agg.failure_rate == 0.0


def test_aggregate_with_failures():
    cases = [
        CaseMetrics(relevance=0.9, failure_type=None),
        CaseMetrics(relevance=0.1, failure_type="empty_response"),
        CaseMetrics(relevance=0.1, failure_type="low_overlap"),
    ]
    agg = aggregate_case_metrics(cases)
    assert agg.failure_count == 2
    assert abs(agg.failure_rate - 2/3) < 0.001
    assert agg.failure_breakdown["empty_response"] == 1
    assert agg.failure_breakdown["low_overlap"] == 1


def test_aggregate_to_dict_keys():
    agg = aggregate_case_metrics([CaseMetrics(relevance=0.5)])
    d = agg.to_dict()
    assert "avg_relevance" in d
    assert "avg_faithfulness" in d
    assert "avg_latency_ms" in d
    assert "total_tokens" in d
    assert "total_cost_usd" in d
    assert "failure_rate" in d
    assert "failure_breakdown" in d


# ---------------------------------------------------------------------------
# CaseMetrics.to_dict
# ---------------------------------------------------------------------------

def test_case_metrics_to_dict():
    m = CaseMetrics(relevance=0.8, faithfulness=0.6, latency_ms=50, token_count=10, cost_usd=0.001)
    d = m.to_dict()
    assert d["relevance"] == 0.8
    assert d["faithfulness"] == 0.6
    assert d["latency_ms"] == 50
    assert d["token_count"] == 10


# ---------------------------------------------------------------------------
# EvaluationService (mock-based)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_evaluation_service_add_case():
    from backend.evaluation.service import EvaluationService

    mock_session = MagicMock()
    mock_case_repo = MagicMock()
    mock_case_repo.add = AsyncMock(side_effect=lambda x: x)
    mock_run_repo = MagicMock()
    mock_snap_repo = MagicMock()

    svc = EvaluationService(session=mock_session)
    svc._case_repo = mock_case_repo
    svc._run_repo = mock_run_repo
    svc._snap_repo = mock_snap_repo

    run_id = uuid.uuid4()
    case = await svc.add_case(
        run_id=run_id,
        question="What is AI?",
        predicted="AI is artificial intelligence.",
        ground_truth="Artificial intelligence.",
        context="AI overview.",
        latency_ms=80.0,
        token_count=30,
    )

    mock_case_repo.add.assert_called_once()
    assert case.question == "What is AI?"
    assert case.run_id == run_id


@pytest.mark.asyncio
async def test_evaluation_service_add_cases_bulk():
    from backend.evaluation.service import EvaluationService

    mock_session = MagicMock()
    mock_case_repo = MagicMock()
    added = []

    async def fake_add(x):
        added.append(x)
        return x

    mock_case_repo.add = fake_add
    svc = EvaluationService(session=mock_session)
    svc._case_repo = mock_case_repo

    run_id = uuid.uuid4()
    cases = [
        {"question": "Q1?", "predicted": "A1", "ground_truth": "A1"},
        {"question": "Q2?", "predicted": "A2"},
    ]
    results = await svc.add_cases_bulk(run_id, cases)
    assert len(results) == 2


@pytest.mark.asyncio
async def test_evaluation_service_compute_aggregate():
    from backend.evaluation.service import EvaluationService

    mock_session = MagicMock()
    mock_case_repo = MagicMock()
    mock_snap_repo = MagicMock()

    case1 = MagicMock()
    case1.case_metrics = {"relevance": 0.8, "faithfulness": 0.7, "latency_ms": 100,
                          "token_count": 50, "cost_usd": 0.001, "failure_type": None}
    case2 = MagicMock()
    case2.case_metrics = {"relevance": 0.6, "faithfulness": 0.5, "latency_ms": 200,
                          "token_count": 80, "cost_usd": 0.002, "failure_type": "low_overlap"}

    mock_case_repo.list_by_run = AsyncMock(return_value=[case1, case2])
    mock_snap_repo.add = AsyncMock(side_effect=lambda x: x)

    svc = EvaluationService(session=mock_session)
    svc._case_repo = mock_case_repo
    svc._snap_repo = mock_snap_repo

    run_id = uuid.uuid4()
    snap = await svc.compute_and_save_aggregate(run_id)

    assert snap.run_id == run_id
    assert snap.snapshot_metrics["case_count"] == 2
    assert snap.snapshot_metrics["failure_count"] == 1
    mock_snap_repo.add.assert_called_once()


@pytest.mark.asyncio
async def test_evaluation_service_ingest_cases_empty():
    from backend.evaluation.service import EvaluationService

    mock_session = MagicMock()
    svc = EvaluationService(session=mock_session)
    assert await svc.ingest_cases(uuid.uuid4(), []) == []


@pytest.mark.asyncio
async def test_evaluation_service_get_latest_snapshot_returns_last():
    from backend.evaluation.service import EvaluationService

    mock_session = MagicMock()
    old = MagicMock()
    old.id = uuid.uuid4()
    new = MagicMock()
    new.id = uuid.uuid4()
    mock_snap_repo = MagicMock()
    mock_snap_repo.list_by_run = AsyncMock(return_value=[old, new])

    svc = EvaluationService(session=mock_session)
    svc._snap_repo = mock_snap_repo

    result = await svc.get_latest_snapshot(uuid.uuid4())
    assert result is new


@pytest.mark.asyncio
async def test_evaluation_service_get_latest_snapshot_empty():
    from backend.evaluation.service import EvaluationService

    mock_session = MagicMock()
    mock_snap_repo = MagicMock()
    mock_snap_repo.list_by_run = AsyncMock(return_value=[])

    svc = EvaluationService(session=mock_session)
    svc._snap_repo = mock_snap_repo

    result = await svc.get_latest_snapshot(uuid.uuid4())
    assert result is None
