"""Unit tests for optional MLflow tracking."""

import sys
from unittest.mock import MagicMock, patch

import pytest

from backend.experiments.tracking.mlflow_tracker import try_log_evaluation_to_mlflow


@pytest.fixture
def mlflow_settings_disabled():
    s = MagicMock()
    s.mlflow_enabled = False
    s.mlflow_tracking_uri = "http://localhost:5000"
    s.mlflow_experiment_name = "vertexops-evaluations"
    return s


@pytest.fixture
def mlflow_settings_enabled():
    s = MagicMock()
    s.mlflow_enabled = True
    s.mlflow_tracking_uri = "http://localhost:5000"
    s.mlflow_experiment_name = "vertexops-evaluations"
    return s


def test_mlflow_skipped_when_disabled(mlflow_settings_disabled):
    with patch(
        "backend.core.config.get_settings",
        return_value=mlflow_settings_disabled,
    ):
        try_log_evaluation_to_mlflow(
            run_id="r1",
            experiment_id="e1",
            metrics={"avg_relevance": 0.5},
            params={"k": "v"},
        )


def test_mlflow_skipped_when_uri_missing(mlflow_settings_enabled):
    mlflow_settings_enabled.mlflow_tracking_uri = None
    with patch(
        "backend.core.config.get_settings",
        return_value=mlflow_settings_enabled,
    ):
        try_log_evaluation_to_mlflow(
            run_id="r1",
            experiment_id="e1",
            metrics={"x": 1.0},
            params={},
        )


def test_mlflow_success_with_stub_module(monkeypatch, mlflow_settings_enabled):
    fake_ml = MagicMock()
    ctx = MagicMock()
    ctx.__enter__ = MagicMock(return_value=None)
    ctx.__exit__ = MagicMock(return_value=None)
    fake_ml.start_run = MagicMock(return_value=ctx)
    monkeypatch.setitem(sys.modules, "mlflow", fake_ml)

    with patch(
        "backend.core.config.get_settings",
        return_value=mlflow_settings_enabled,
    ):
        try_log_evaluation_to_mlflow(
            run_id="r1",
            experiment_id="e1",
            metrics={"avg_relevance": 0.5},
            params={"eval_kind": "evaluation"},
        )

    fake_ml.set_tracking_uri.assert_called_once()
    fake_ml.set_experiment.assert_called_once_with("vertexops-evaluations")
    fake_ml.start_run.assert_called_once()
    assert fake_ml.log_param.call_count >= 1
    fake_ml.log_metric.assert_called()


def test_mlflow_swallows_runtime_errors(monkeypatch, mlflow_settings_enabled):
    fake_ml = MagicMock()
    fake_ml.set_tracking_uri = MagicMock(side_effect=RuntimeError("unreachable"))
    monkeypatch.setitem(sys.modules, "mlflow", fake_ml)

    with patch(
        "backend.core.config.get_settings",
        return_value=mlflow_settings_enabled,
    ):
        try_log_evaluation_to_mlflow(
            run_id="r1",
            experiment_id="e1",
            metrics={"m": 1.0},
            params={},
        )
