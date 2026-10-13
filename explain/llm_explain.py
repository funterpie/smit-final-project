"""explain/llm_explain.py — Groq LLM explanation layer with local fallback.

DESIGN RULES (AGENTS.md — do NOT loosen):
  1. NEVER receive the raw diff — only computed signals + retrieved evidence.
  2. If Groq API fails (network, quota, missing key), fall back to a
     locally-generated plain-English summary — never raise an exception.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from models.risk_engine import RiskReport
from rag.retrieve import RetrievedEvidence


@dataclass
class Explanation:
    """LLM-generated (or fallback) plain-English explanation of the risk score."""

    text: str
    source: str  # "groq" | "local_fallback"


# ---------------------------------------------------------------------------
# Local fallback generator (no API needed)
# ---------------------------------------------------------------------------

def _local_fallback(report: RiskReport, evidence: RetrievedEvidence | None) -> str:
    """Generate a plain-English explanation from signal data alone (no LLM)."""
    triggered = report.triggered_signals()

    if not triggered:
        base = (
            f"This commit has a low risk score of {report.score}/100. "
            "No risk signals were triggered: the diff is small, no sensitive modules "
            "are touched, the author has a clean track record, and tests are present."
        )
    else:
        signal_descs = "\n".join(f"  • {s.name}: {s.description}" for s in triggered)
        base = (
            f"This commit has a risk score of {report.score}/100, "
            f"driven by {len(triggered)} triggered signal(s):\n{signal_descs}\n\n"
            "Suggestion: consider reviewing these areas carefully before merging."
        )

    if evidence:
        base += (
            f"\n\nSimilar past bug-inducing commit found (similarity={evidence.similarity:.2f}): "
            f"{evidence.summary} [commit: {evidence.commit_hash}]."
        )
    else:
        base += "\n\nNo closely matching past bug-inducing commits found in the index."

    return base


# ---------------------------------------------------------------------------
# Groq call
# ---------------------------------------------------------------------------

def _groq_explain(
    report: RiskReport,
    evidence: RetrievedEvidence | None,
    api_key: str,
) -> str:
    """Call Groq API (llama3-8b-8192) and return explanation text.

    Raises:
        Exception: on any API failure (caller catches and falls back).
    """
    from groq import Groq  # type: ignore

    triggered = report.triggered_signals()
    signal_text = (
        "\n".join(f"- {s.name} (weight {s.weight}): {s.description}" for s in triggered)
        if triggered
        else "None"
    )
    evidence_text = (
        f"Similar past bug commit (similarity={evidence.similarity:.2f}): {evidence.summary}"
        if evidence
        else "No similar past bug-inducing commits found."
    )

    prompt = (
        "You are a senior software engineer reviewing a git commit for risk. "
        "You have been given the following pre-computed risk signals (NOT the raw code diff). "
        "Your job is to write a concise, plain-English explanation (3-5 sentences) of WHY "
        "this commit is risky and what the reviewer should specifically look for. "
        "Only use the information provided — do NOT hallucinate code details.\n\n"
        f"Risk Score: {report.score}/100\n\n"
        f"Triggered signals:\n{signal_text}\n\n"
        f"RAG evidence: {evidence_text}\n\n"
        "Explanation and suggestion:"
    )

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=256,
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def explain_risk(
    report: RiskReport,
    evidence: RetrievedEvidence | None,
    groq_api_key: str = "",
) -> Explanation:
    """Generate a plain-English explanation of the risk score.

    Args:
        report: RiskReport from compute_risk(). Contains score + signals.
        evidence: Optional RAG match. None if no match above threshold.
        groq_api_key: Groq API key. Empty string → use local fallback immediately.

    Returns:
        Explanation with text and source ("groq" or "local_fallback").

    Design note:
        The raw diff is NEVER passed here — only signals and evidence summary.
    """
    if not groq_api_key:
        return Explanation(text=_local_fallback(report, evidence), source="local_fallback")

    try:
        text = _groq_explain(report, evidence, groq_api_key)
        return Explanation(text=text, source="groq")
    except Exception as exc:
        # Any API failure → graceful fallback
        fallback_text = (
            f"[Groq API unavailable: {type(exc).__name__}] "
            + _local_fallback(report, evidence)
        )
        return Explanation(text=fallback_text, source="local_fallback")
