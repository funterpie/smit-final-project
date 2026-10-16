"""tests/test_rag.py — Tests for rag/retrieve.py (no real index needed)."""

import json
import tempfile
from pathlib import Path

import numpy as np
import pytest

from typing import Union

from features.schema import CommitFeatures
from rag.retrieve import RetrievedEvidence, retrieve_evidence


def _sample_features(**overrides: Union[bool, float, int]) -> CommitFeatures:
    base: dict[str, Union[bool, float, int]] = dict(
        lines_added=50, lines_removed=10, files_touched=3,
        dispersion=1.5, author_bug_rate=0.1,
        hours_since_last_commit=24.0, tests_added=True,
        touches_sensitive_module=False,
    )
    base.update(overrides)
    return CommitFeatures(**base)  # type: ignore[arg-type]


class TestRetrievedEvidence:
    def test_dataclass_fields(self) -> None:
        ev = RetrievedEvidence(commit_hash="abc123", similarity=0.9, summary="Test")
        assert ev.commit_hash == "abc123"
        assert ev.similarity == 0.9


class TestRetrieveEvidenceMissingIndex:
    def test_returns_none_when_index_missing(self) -> None:
        """retrieve_evidence must return None gracefully if the index doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = retrieve_evidence(
                _sample_features(),
                index_dir=tmpdir,
                threshold=0.75,
            )
        assert result is None


class TestRetrieveEvidenceWithIndex:
    """Build a tiny FAISS index in a temp dir and verify retrieval works."""

    @pytest.fixture()
    def tiny_index_dir(self, tmp_path: Path) -> Path:
        """Create a minimal FAISS index for testing without network calls."""
        try:
            import faiss
            import numpy as np
        except ImportError:
            pytest.skip("faiss-cpu not installed")

        dim = 8  # tiny dimension for testing
        vectors = np.random.rand(5, dim).astype(np.float32)
        # L2-normalize
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        vectors = vectors / norms

        index = faiss.IndexFlatIP(dim)
        index.add(vectors)
        faiss.write_index(index, str(tmp_path / "index.faiss"))

        metadata = [
            {"commit_id": f"commit_{i}", "project": "test", "summary": f"Bug commit {i}"}
            for i in range(5)
        ]
        (tmp_path / "metadata.json").write_text(json.dumps(metadata))
        return tmp_path

    def test_returns_none_below_threshold(self, tiny_index_dir: Path) -> None:
        """With a very high threshold the retriever should return None."""
        # Monkey-patch the SentenceTransformer to return a fixed tiny vector
        import unittest.mock as mock
        dim = 8
        fake_vec = np.random.rand(1, dim).astype(np.float32)
        fake_vec = fake_vec / np.linalg.norm(fake_vec)

        with mock.patch("rag.retrieve.SentenceTransformer") as mock_st:
            instance = mock_st.return_value
            instance.encode.return_value = fake_vec
            result = retrieve_evidence(
                _sample_features(),
                index_dir=str(tiny_index_dir),
                threshold=0.9999,  # impossibly high threshold
            )
        # Should return None (similarity < 0.9999)
        assert result is None
