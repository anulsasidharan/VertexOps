"""Deterministic evaluation dataset helpers (no live LLM)."""

from typing import Any


def build_synthetic_eval_cases_from_chunk_texts(
    chunk_texts: list[str],
    *,
    max_cases: int = 50,
) -> list[dict[str, Any]]:
    """Derive simple Q/A-style eval rows from corpus chunk strings.

    Used for offline or smoke evaluation when no curated set exists.
    ``predicted`` is left empty for a runner to fill via RAG.
    """
    out: list[dict[str, Any]] = []
    for i, raw in enumerate(chunk_texts):
        if len(out) >= max_cases:
            break
        snippet = (raw or "").strip()
        if not snippet:
            continue
        snippet = snippet[:2000]
        stop = snippet.find(".")
        first_sentence = snippet[: stop + 1] if stop >= 0 else snippet[:200]
        if not first_sentence.strip():
            first_sentence = snippet[:200]
        out.append(
            {
                "question": f"What is the main point of excerpt {i}?",
                "ground_truth": first_sentence.strip(),
                "predicted": "",
                "context": snippet,
            }
        )
    return out
