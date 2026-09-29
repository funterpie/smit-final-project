"""rag/build_index.py — Stub for FAISS index builder over curated bug-inducing commits.

Real implementation: Week 3 (see PLANNING.md).
Uses FAISS (faiss-cpu); do NOT switch to ChromaDB without reading the version-pinning
risk note in PLANNING.md first.
"""

from pathlib import Path


def build_index(
    commits_jsonl_path: str,
    index_output_dir: str,
    embedding_model: str = "microsoft/codebert-base",
) -> None:
    """Embed a curated subset of bug-inducing commits and save a FAISS index.

    Args:
        commits_jsonl_path: Path to a JSONL file where each line is a commit record
            (features only — no raw diff); typically from the curated ApacheJIT subset.
        index_output_dir: Directory where the FAISS index and metadata will be saved.
        embedding_model: HuggingFace model name used to encode commit features.

    Notes:
        - Do NOT embed the full 100k+ ApacheJIT dataset — use the curated subset only.
        - The index directory is read at retrieval time by rag.retrieve.

    Raises:
        NotImplementedError: Always — not yet implemented.
    """
    raise NotImplementedError("build_index() — see PLANNING.md Week 3.")
