"""explain/llm_explain.py — Stub for Groq LLM explanation layer.

DESIGN RULES (from AGENTS.md — do not loosen these):
  1. This function MUST NEVER receive the raw diff — only computed signals + retrieved
     evidence. This enforces privacy and prevents LLM hallucination about the code.
  2. If the Groq API call fails (network, quota, missing key), fall back to a
     locally-generated plain-English summary rather than raising an exception.

Real implementation: Week 3 (see PLANNING.md).
"""

from __future__ import annotations

from dataclasses import dataclass

from models.risk_engine import RiskReport
from rag.retrieve import RetrievedEvidence


@dataclass
class Explanation:
    """LLM-generated plain-English explanation of the risk score."""

    text: str
    source: str  # "groq" | "local_fallback"


def explain_risk(
    report: RiskReport,
    evidence: RetrievedEvidence | None,
    groq_api_key: str,
) -> Explanation:
    """Generate a plain-English explanation of the risk score.

    Args:
        report: The RiskReport produced by models.risk_engine.compute_risk().
            Contains the score and all named signals.
        evidence: Optional RAG-retrieved similar past commit. Pass None if the
            retriever returned no match above the similarity threshold.
        groq_api_key: Groq API key. If empty or falsy, skip the API call and
            use the local fallback immediately.

    Returns:
        An Explanation with the generated text and its source ("groq" or
        "local_fallback").

    Raises:
        NotImplementedError: Always — not yet implemented.

    Note:
        The raw diff MUST NOT be passed here. Only the signals in ``report``
        and the evidence summary are visible to the LLM.
    """
    raise NotImplementedError("explain_risk() — see PLANNING.md Week 3.")
