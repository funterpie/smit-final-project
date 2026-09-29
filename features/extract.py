"""features/extract.py — Stub for PyDriller-based diff feature extraction.

Real implementation will be added in Week 1 (see PLANNING.md).
"""

from features.schema import CommitFeatures


def extract_features(repo_path: str, commit_hash: str) -> CommitFeatures:
    """Extract risk-relevant features from a single commit.

    Args:
        repo_path: Absolute or relative path to the local git repository.
        commit_hash: Full or short SHA of the commit to analyse.

    Returns:
        A populated CommitFeatures instance.

    Raises:
        NotImplementedError: Always — real extraction not yet implemented.
    """
    raise NotImplementedError(
        "extract_features() is not yet implemented. "
        "See PLANNING.md Week 1 for the PyDriller-based implementation plan."
    )
