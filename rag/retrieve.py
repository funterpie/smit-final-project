"""rag/retrieve.py — FAISS similarity search with similarity threshold.

Design rules (AGENTS.md):
  - MUST return None when no commit exceeds `threshold`.
  - Never force a top-k result if nothing is actually similar.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

sys.path.insert(0, str(Path(__file__).parent.parent))


@dataclass
class RetrievedEvidence:
    """A matched bug-inducing commit returned by the RAG retriever."""

    commit_hash: str
    similarity: float
    summary: str  # human-readable one-line description of the matched commit


def _build_query_text(features: object) -> str:
    """Convert CommitFeatures to the same text format used during indexing."""
    from features.schema import CommitFeatures
    assert isinstance(features, CommitFeatures)
    return (
        f"project=unknown "
        f"lines_added={features.lines_added} "
        f"lines_removed={features.lines_removed} "
        f"files={features.files_touched} "
        f"dispersion={features.dispersion:.2f} "
        f"author_bug_rate={features.author_bug_rate:.2f} "
        f"hours_since_last={features.hours_since_last_commit:.1f} "
        f"tests_added={features.tests_added} "
        f"sensitive={features.touches_sensitive_module}"
    )


def retrieve_evidence(
    features: object,
    index_dir: str | None = None,
    threshold: float | None = None,
) -> RetrievedEvidence | None:
    """Search the FAISS index for the most similar bug-inducing past commit.

    Args:
        features: CommitFeatures of the commit being reviewed.
        index_dir: Directory containing index.faiss + metadata.json.
            Defaults to config.INDEX_DIR.
        threshold: Minimum cosine similarity for a match. Defaults to
            config.SIMILARITY_THRESHOLD. Returns None if nothing qualifies.

    Returns:
        RetrievedEvidence if a match is found, else None.
    """
    from config import INDEX_DIR, SIMILARITY_THRESHOLD

    idx_dir = Path(index_dir) if index_dir else INDEX_DIR
    sim_threshold = threshold if threshold is not None else SIMILARITY_THRESHOLD

    index_path = idx_dir / "index.faiss"
    meta_path = idx_dir / "metadata.json"

    if not index_path.exists() or not meta_path.exists():
        # Index not built yet — return None gracefully
        return None

    index = faiss.read_index(str(index_path))
    with meta_path.open() as fh:
        metadata: list[dict] = json.load(fh)

    model = SentenceTransformer("all-MiniLM-L6-v2")
    query_text = _build_query_text(features)
    query_vec: np.ndarray = model.encode(
        [query_text], normalize_embeddings=True
    ).astype(np.float32)

    # Search top-1
    distances, indices = index.search(query_vec, k=1)
    similarity = float(distances[0][0])
    idx = int(indices[0][0])

    if similarity < sim_threshold:
        return None

    meta = metadata[idx]
    return RetrievedEvidence(
        commit_hash=meta.get("commit_id", "unknown"),
        similarity=round(similarity, 4),
        summary=meta.get("summary", "No summary available."),
    )
