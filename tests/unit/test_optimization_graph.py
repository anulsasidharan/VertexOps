"""Unit tests for LangGraph optimization workflow."""

import pytest

pytest.importorskip("langgraph")

from backend.orchestration.optimization_graph import build_optimization_graph


def test_graph_roll_back_on_regression():
    graph = build_optimization_graph()
    out = graph.invoke(
        {
            "iteration": 1,
            "max_iterations": 5,
            "best_score": 0.8,
            "trial_score": 0.5,
            "current_config": {"top_k": 10},
            "best_config": {"top_k": 8},
            "failure_breakdown": {"low_overlap": 3},
        }
    )
    assert out["rollback_reason"] == "regression_vs_best"
    assert out["current_config"]["top_k"] == 8


def test_graph_updates_best_on_improvement():
    graph = build_optimization_graph()
    out = graph.invoke(
        {
            "iteration": 1,
            "max_iterations": 5,
            "best_score": 0.6,
            "trial_score": 0.75,
            "current_config": {"top_k": 6},
            "best_config": {"top_k": 5},
            "failure_breakdown": {},
        }
    )
    assert out.get("rollback_reason", "") == ""
    assert out["best_score"] == 0.75
    assert out["best_config"]["top_k"] >= 6


def test_graph_custom_strategy_fn():
    graph = build_optimization_graph(strategy_fn=lambda _s: "raise_temperature")
    out = graph.invoke(
        {
            "iteration": 0,
            "max_iterations": 3,
            "best_score": 0.0,
            "trial_score": 0.0,
            "current_config": {"temperature": 0.2},
            "best_config": {},
            "failure_breakdown": {"x": 1},
        }
    )
    assert out["last_strategy"] == "raise_temperature"
    assert out["current_config"]["temperature"] > 0.2
