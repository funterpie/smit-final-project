"""models/baseline.py — Stub for logistic regression / random forest baseline.

Real implementation: Week 1, after ApacheJIT feature extraction (see PLANNING.md).
"""

from features.schema import CommitFeatures


def train_baseline(features_csv_path: str, labels_csv_path: str) -> None:
    """Train a logistic regression and random forest baseline on extracted features.

    Args:
        features_csv_path: Path to a CSV of CommitFeatures rows.
        labels_csv_path: Path to a CSV of binary bug-inducing labels (0/1).

    Raises:
        NotImplementedError: Always — not yet implemented.
    """
    raise NotImplementedError("train_baseline() — see PLANNING.md Week 1.")


def predict_baseline(features: CommitFeatures) -> float:
    """Return the baseline model's bug-inducing probability for one commit.

    Args:
        features: Structured commit features.

    Returns:
        Probability in [0.0, 1.0] that the commit is bug-inducing.

    Raises:
        NotImplementedError: Always — not yet implemented.
    """
    raise NotImplementedError("predict_baseline() — see PLANNING.md Week 1.")
