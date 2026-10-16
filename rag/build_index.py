"""rag/build_index.py — FAISS index builder for curated bug-inducing commits.

Usage:
    python -m rag.build_index [--commits path/to/bug_inducing_commits.jsonl]

Reads a JSONL file (output of scripts/prepare_dataset.py), embeds each record
using sentence-transformers (all-MiniLM-L6-v2 — fast, small, local-only), and
saves a FAISS flat-L2 index + metadata JSON to the configured index directory.

Why all-MiniLM-L6-v2 instead of CodeBERT for RAG?
    Embedding 500-5000 records with CodeBERT is slow (~1.5 GB VRAM).
    MiniLM is 80 MB and runs on CPU in seconds. Similarity of feature
    vectors (numerical + textual summary) is sufficient for retrieval.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt

sys.path.insert(0, str(Path(__file__).parent.parent))

EMBEDDING_DIM = 384  # all-MiniLM-L6-v2 output dim


def _build_text_repr(record: dict[str, Any]) -> str:
    """Convert a bug-inducing commit record to a short text for embedding."""
    return (
        f"project={record.get('project', 'unknown')} "
        f"lines_added={record.get('lines_added', 0)} "
        f"lines_removed={record.get('lines_removed', 0)} "
        f"files={record.get('files_touched', 0)} "
        f"dispersion={record.get('dispersion', 0.0):.2f} "
        f"author_bug_rate={record.get('author_bug_rate', 0.0):.2f} "
        f"hours_since_last={record.get('hours_since_last_commit', 0.0):.1f} "
        f"tests_added={record.get('tests_added', False)} "
        f"sensitive={record.get('touches_sensitive_module', False)}"
    )


def build_index(
    commits_jsonl_path: str,
    index_output_dir: str | None = None,
    embedding_model: str = "all-MiniLM-L6-v2",
    batch_size: int = 64,
) -> None:
    """Embed curated bug-inducing commits and save a FAISS flat index.

    Args:
        commits_jsonl_path: Path to JSONL file (one record per line).
        index_output_dir: Where to save index.faiss + metadata.json.
            Defaults to config.INDEX_DIR.
        embedding_model: SentenceTransformer model name.
        batch_size: Encoding batch size.
    """
    import faiss
    from sentence_transformers import SentenceTransformer

    from config import INDEX_DIR

    out_dir = Path(index_output_dir) if index_output_dir else INDEX_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    jsonl_path = Path(commits_jsonl_path)
    records: list[dict[str, Any]] = []
    with jsonl_path.open() as fh:
        for line in fh:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    print(f"[rag.build_index] Loaded {len(records):,} bug-inducing commits from {jsonl_path}")

    model = SentenceTransformer(embedding_model)
    texts = [_build_text_repr(r) for r in records]

    print(f"[rag.build_index] Encoding with {embedding_model}...")
    embeddings: npt.NDArray[np.float32] = model.encode(
        texts, batch_size=batch_size, show_progress_bar=True, normalize_embeddings=True
    )
    print(f"[rag.build_index] Embeddings shape: {embeddings.shape}")

    # FAISS inner-product index (cosine similarity, since embeddings are L2-normalised)
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings.astype(np.float32))
    print(f"[rag.build_index] FAISS index contains {index.ntotal:,} vectors.")

    index_path = out_dir / "index.faiss"
    meta_path = out_dir / "metadata.json"

    faiss.write_index(index, str(index_path))

    # Store metadata (commit_id, project, summary) for display at retrieval time
    metadata = [
        {
            "commit_id": r.get("commit_id", ""),
            "project": r.get("project", ""),
            "summary": r.get("summary", _build_text_repr(r)),
        }
        for r in records
    ]
    with meta_path.open("w") as fh:
        json.dump(metadata, fh, indent=2)

    print(f"[rag.build_index] Saved index → {index_path}")
    print(f"[rag.build_index] Saved metadata → {meta_path}")
    print("[rag.build_index] Done.")


if __name__ == "__main__":
    import argparse

    DATA_PROCESSED = Path(__file__).parent.parent / "data" / "processed"

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--commits",
        default=str(DATA_PROCESSED / "bug_inducing_commits.jsonl"),
        help="Path to bug-inducing commits JSONL.",
    )
    parser.add_argument("--index-dir", default=None, help="Output index directory.")
    args = parser.parse_args()

    build_index(args.commits, args.index_dir)
