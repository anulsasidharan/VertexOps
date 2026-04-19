"""Metric computation for evaluation cases — relevance, faithfulness, latency, cost."""

import re
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class CaseMetrics:
    """Per-case metrics computed after a single evaluation case executes."""

    relevance: float = 0.0  # 0-1: how relevant the answer is to the question
    faithfulness: float = 0.0  # 0-1: how faithfully answer reflects context
    latency_ms: float = 0.0
    token_count: int = 0
    cost_usd: float = 0.0
    failure_type: Optional[str] = None
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "relevance": self.relevance,
            "faithfulness": self.faithfulness,
            "latency_ms": self.latency_ms,
            "token_count": self.token_count,
            "cost_usd": self.cost_usd,
            "failure_type": self.failure_type,
            **self.extra,
        }


@dataclass
class AggregateMetrics:
    """Aggregate metrics across all cases in a run."""

    case_count: int = 0
    avg_relevance: float = 0.0
    avg_faithfulness: float = 0.0
    avg_latency_ms: float = 0.0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    failure_count: int = 0
    failure_rate: float = 0.0
    failure_breakdown: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_count": self.case_count,
            "avg_relevance": round(self.avg_relevance, 4),
            "avg_faithfulness": round(self.avg_faithfulness, 4),
            "avg_latency_ms": round(self.avg_latency_ms, 2),
            "total_tokens": self.total_tokens,
            "total_cost_usd": round(self.total_cost_usd, 6),
            "failure_count": self.failure_count,
            "failure_rate": round(self.failure_rate, 4),
            "failure_breakdown": self.failure_breakdown,
        }


def _token_overlap(a: str, b: str) -> float:
    """Jaccard token overlap as a lightweight relevance proxy."""
    ta = set(re.findall(r"\w+", a.lower()))
    tb = set(re.findall(r"\w+", b.lower()))
    if not ta and not tb:
        return 1.0
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def compute_case_metrics(
    question: str,
    predicted: str,
    ground_truth: Optional[str],
    context: Optional[str],
    latency_ms: float = 0.0,
    token_count: int = 0,
    cost_per_1k_tokens: float = 0.002,
) -> CaseMetrics:
    """Compute heuristic per-case metrics without an external judge model."""
    relevance = _token_overlap(question, predicted) if predicted else 0.0
    faithfulness = _token_overlap(context or "", predicted) if predicted and context else 0.0

    failure_type: Optional[str] = None
    if not predicted or not predicted.strip():
        failure_type = "empty_response"
    elif ground_truth and _token_overlap(predicted, ground_truth) < 0.05:
        failure_type = "low_overlap"

    cost_usd = (token_count / 1000) * cost_per_1k_tokens

    return CaseMetrics(
        relevance=round(relevance, 4),
        faithfulness=round(faithfulness, 4),
        latency_ms=latency_ms,
        token_count=token_count,
        cost_usd=round(cost_usd, 6),
        failure_type=failure_type,
    )


def aggregate_case_metrics(cases: list[CaseMetrics]) -> AggregateMetrics:
    """Roll up per-case metrics into a run-level summary."""
    n = len(cases)
    if n == 0:
        return AggregateMetrics()

    failures = [c for c in cases if c.failure_type is not None]
    breakdown: dict[str, int] = {}
    for c in failures:
        breakdown[c.failure_type] = breakdown.get(c.failure_type, 0) + 1  # type: ignore[index]

    return AggregateMetrics(
        case_count=n,
        avg_relevance=sum(c.relevance for c in cases) / n,
        avg_faithfulness=sum(c.faithfulness for c in cases) / n,
        avg_latency_ms=sum(c.latency_ms for c in cases) / n,
        total_tokens=sum(c.token_count for c in cases),
        total_cost_usd=sum(c.cost_usd for c in cases),
        failure_count=len(failures),
        failure_rate=len(failures) / n,
        failure_breakdown=breakdown,
    )
