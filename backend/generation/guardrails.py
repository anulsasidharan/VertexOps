"""Prompt-injection guardrails and output safety for RAG pipelines."""

import re
from dataclasses import dataclass
from typing import List, Optional


# ---------------------------------------------------------------------------
# Injection detection
# ---------------------------------------------------------------------------

_INJECTION_PATTERNS: List[re.Pattern] = [
    # Classic role override attempts
    re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?", re.IGNORECASE),
    re.compile(r"disregard\s+(all\s+)?(previous|prior|above)\s+instructions?", re.IGNORECASE),
    re.compile(r"forget\s+(all\s+)?(previous|prior|above)\s+instructions?", re.IGNORECASE),
    # System-prompt hijacking
    re.compile(r"\bsystem\s*prompt\b.*?\boverride\b", re.IGNORECASE | re.DOTALL),
    re.compile(r"\bnew\s+role\b", re.IGNORECASE),
    re.compile(r"\byou\s+are\s+now\b", re.IGNORECASE),
    re.compile(r"\bact\s+as\s+(?:a\s+)?(?:new|different|evil|unconstrained)\b", re.IGNORECASE),
    # Data exfiltration probes
    re.compile(r"\brepeat\s+(everything|all)\s+(you\s+)?(know|have|were\s+told)\b", re.IGNORECASE),
    re.compile(r"\bprint\s+(your\s+)?(system\s+)?instructions?\b", re.IGNORECASE),
    # Jailbreak markers
    re.compile(r"\bdan\b.*\bjailbreak\b", re.IGNORECASE),
    re.compile(r"\bdo\s+anything\s+now\b", re.IGNORECASE),
]


@dataclass
class GuardrailResult:
    is_safe: bool
    risk_level: str  # "none" | "low" | "medium" | "high"
    reasons: List[str]

    @classmethod
    def safe(cls) -> "GuardrailResult":
        return cls(is_safe=True, risk_level="none", reasons=[])

    @classmethod
    def unsafe(cls, reasons: List[str], risk_level: str = "high") -> "GuardrailResult":
        return cls(is_safe=False, risk_level=risk_level, reasons=reasons)


def check_injection(text: str) -> GuardrailResult:
    """Scan text for prompt-injection patterns.

    Returns GuardrailResult(is_safe=False) if any pattern fires.
    """
    reasons: List[str] = []
    for pattern in _INJECTION_PATTERNS:
        if pattern.search(text):
            reasons.append(f"Matched injection pattern: {pattern.pattern[:60]}")

    if reasons:
        return GuardrailResult.unsafe(reasons, risk_level="high")
    return GuardrailResult.safe()


# ---------------------------------------------------------------------------
# Chunk sanitization
# ---------------------------------------------------------------------------

_MAX_CHUNK_LEN = 4096  # characters


def sanitize_chunk(text: str) -> str:
    """Light sanitization of a retrieved chunk before prompt assembly.

    - Strips null bytes and control characters (except newlines/tabs)
    - Truncates excessively long chunks
    """
    # Remove null bytes and control chars except \n and \t
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", " ", text)
    text = text.strip()
    if len(text) > _MAX_CHUNK_LEN:
        text = text[:_MAX_CHUNK_LEN] + "…"
    return text


def sanitize_chunks(chunks: List[str]) -> List[str]:
    return [sanitize_chunk(c) for c in chunks]


# ---------------------------------------------------------------------------
# Output safety
# ---------------------------------------------------------------------------

_UNSAFE_OUTPUT_PATTERNS: List[re.Pattern] = [
    # Potential credential leakage
    re.compile(r"\b(?:password|secret|api[_\s]?key)\s*[:=]\s*\S+", re.IGNORECASE),
    # PII patterns — SSN, credit card (simplified)
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),                   # SSN
    re.compile(r"\b(?:4\d{12}(?:\d{3})?|5[1-5]\d{14})\b"),  # Visa/MC (rough)
]


def check_output_safety(answer: str) -> GuardrailResult:
    """Scan generated answer for potentially unsafe content."""
    reasons: List[str] = []
    for pattern in _UNSAFE_OUTPUT_PATTERNS:
        if pattern.search(answer):
            reasons.append(f"Potential unsafe output: {pattern.pattern[:60]}")

    if reasons:
        return GuardrailResult.unsafe(reasons, risk_level="medium")
    return GuardrailResult.safe()


def redact_unsafe_output(answer: str) -> str:
    """Redact matched unsafe patterns from the answer in-place."""
    for pattern in _UNSAFE_OUTPUT_PATTERNS:
        answer = pattern.sub("[REDACTED]", answer)
    return answer
