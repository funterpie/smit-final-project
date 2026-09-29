"""rag/retrieve.py — Stub for FAISS similarity search with similarity threshold.

Design rule (from AGENTS.md):
  - MUST return None when no commit exceeds the similarity threshold.
  - Never force a top-k result if nothing is actually similar.

Real implementation: Week 3 (see PLANNING.md).
"""

from __future__ import annotations

from dataclasses import dataclass

from features.schema import CommitFeatures


@dataclass
class RetrievedEvidence:
    """A matched bug-inducing commit returned by the RAG retriever."""

    commit_hash: str
    similarity: float
    summary: str  # human-readable one-line description of the matched commit


def retrieve_evidence(
    features: CommitFeatures,
    index_dir: str,
    threshold: float,
) -> RetrievedEvidence | None:
    """Search the FAISS index for the most similar bug-inducing past commit.

    Args:
        features: Structured features of the commit being reviewed.
        index_dir: Directory containing the pre-built FAISS index.
        threshold: Minimum cosine similarity required to return a match.
            Commits below this threshold return None ("no match found").

    Returns:
        A RetrievedEvidence instance if a match exceeds the threshold,
        or None if no sufficiently similar past commit exists.

    Raises:
        NotImplementedError: Always — not yet implemented.
    """
    raise NotImplementedError("retrieve_evidence() — see PLANNING.md Week 3.")
