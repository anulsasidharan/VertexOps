"""Unit tests for OrchestrationService persistence."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

pytest.importorskip("langgraph")

from backend.orchestration.service import OrchestrationService


@pytest.mark.asyncio
async def test_propose_and_record_iteration_persists_steps():
    run_id = uuid.uuid4()
    mock_run = MagicMock()
    mock_run.run_logs = {"kind": "evaluation"}

    mock_repo = MagicMock()
    mock_repo.get = AsyncMock(return_value=mock_run)

    mock_session = MagicMock()
    mock_session.flush = AsyncMock()
    svc = OrchestrationService(session=mock_session)
    svc._run_repo = mock_repo

    result = await svc.propose_and_record_iteration(
        run_id,
        failure_breakdown={"low_overlap": 2},
        trial_score=0.4,
        current_config={"top_k": 8},
        best_score=0.7,
        best_config={"top_k": 6},
        iteration=2,
        max_iterations=5,
    )

    assert "last_strategy" in result
    mock_repo.get.assert_awaited_once_with(run_id)
    assert "orchestration" in mock_run.run_logs
    assert len(mock_run.run_logs["orchestration"]["steps"]) == 1
    assert mock_run.run_logs["orchestration"]["steps"][0]["iteration"] == 2


@pytest.mark.asyncio
async def test_propose_and_record_missing_run_no_crash():
    mock_repo = MagicMock()
    mock_repo.get = AsyncMock(return_value=None)

    mock_session = MagicMock()
    mock_session.flush = AsyncMock()
    svc = OrchestrationService(session=mock_session)
    svc._run_repo = mock_repo

    result = await svc.propose_and_record_iteration(
        uuid.uuid4(),
        failure_breakdown={},
        trial_score=0.1,
        current_config={"top_k": 5},
        best_score=0.0,
        best_config={},
        iteration=0,
        max_iterations=3,
    )
    assert isinstance(result, dict)
