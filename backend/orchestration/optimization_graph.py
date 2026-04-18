"""LangGraph workflow for bounded strategy updates and rollback."""

from typing import Any, Callable, Dict, Optional, TypedDict

from langgraph.graph import END, START, StateGraph


class OptimizationState(TypedDict, total=False):
    """State passed through the optimization graph."""

    iteration: int
    max_iterations: int
    current_config: Dict[str, Any]
    best_config: Dict[str, Any]
    best_score: float
    trial_score: float
    failure_breakdown: Dict[str, int]
    last_strategy: str
    rollback_reason: str
    failure_category: str


StrategyFn = Optional[Callable[[OptimizationState], str]]


def _default_failure_category(state: OptimizationState) -> str:
    fb = state.get("failure_breakdown") or {}
    if not fb:
        return "none"
    return max(fb.items(), key=lambda kv: kv[1])[0]


def _analyze_failures(
    state: OptimizationState, strategy_fn: StrategyFn
) -> OptimizationState:
    cat = _default_failure_category(state)
    if strategy_fn is not None:
        strat = strategy_fn(state)
    elif cat in ("empty_response",):
        strat = "raise_temperature"
    elif cat in ("low_overlap",):
        strat = "increase_top_k"
    else:
        strat = "increase_top_k"
    return {"failure_category": cat, "last_strategy": strat}


def _propose_config(state: OptimizationState) -> OptimizationState:
    cfg = dict(state.get("current_config") or {})
    strat = state.get("last_strategy", "increase_top_k")
    if strat == "increase_top_k":
        cfg["top_k"] = min(int(cfg.get("top_k", 5)) + 2, 20)
    elif strat == "raise_temperature":
        cfg["temperature"] = min(float(cfg.get("temperature", 0.2)) + 0.1, 1.0)
    return {"current_config": cfg}


def _gate_and_rollback(state: OptimizationState) -> OptimizationState:
    trial = float(state.get("trial_score", 0.0))
    best = float(state.get("best_score", 0.0))
    best_cfg = dict(state.get("best_config") or {})
    cur_cfg = dict(state.get("current_config") or {})
    if best > 0 and trial < best * 0.90:
        return {
            "current_config": best_cfg or cur_cfg,
            "rollback_reason": "regression_vs_best",
        }
    if trial >= best:
        return {
            "best_score": trial,
            "best_config": cur_cfg,
            "rollback_reason": "",
        }
    return {"rollback_reason": ""}


def build_optimization_graph(
    strategy_fn: StrategyFn = None,
) -> Any:
    """Compile a small linear graph: analyze → propose → gate."""

    def analyze(state: OptimizationState) -> OptimizationState:
        return _analyze_failures(state, strategy_fn)

    graph = StateGraph(OptimizationState)
    graph.add_node("analyze", analyze)
    graph.add_node("propose", _propose_config)
    graph.add_node("gate", _gate_and_rollback)
    graph.add_edge(START, "analyze")
    graph.add_edge("analyze", "propose")
    graph.add_edge("propose", "gate")
    graph.add_edge("gate", END)
    return graph.compile()
