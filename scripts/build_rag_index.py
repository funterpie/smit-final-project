"""scripts/build_rag_index.py — Quick entry point to build the FAISS RAG index.

Usage:
    python scripts/build_rag_index.py

Requires:
    - data/processed/bug_inducing_commits.jsonl (run train_baseline.py first)
    - sentence-transformers installed (pip install sentence-transformers)
    - faiss-cpu installed (pip install faiss-cpu)
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

DATA_PROCESSED = Path(__file__).parent.parent / "data" / "processed"
JSONL_PATH = DATA_PROCESSED / "bug_inducing_commits.jsonl"


def main() -> None:
    if not JSONL_PATH.exists():
        print(f"[build_rag_index] {JSONL_PATH} not found.")
        print("  Run: python scripts/train_baseline.py first.")
        sys.exit(1)

    from rag.build_index import build_index
    build_index(str(JSONL_PATH))


if __name__ == "__main__":
    main()
