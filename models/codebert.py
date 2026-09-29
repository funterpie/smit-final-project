"""models/codebert.py — Stub for CodeBERT fine-tuning and inference.

Real implementation: Week 2 on Colab free tier with Drive checkpointing.
Training script must support resume-from-checkpoint (sessions can disconnect).
"""

from features.schema import CommitFeatures


def fine_tune_codebert(
    train_data_path: str,
    checkpoint_dir: str,
    num_epochs: int = 5,
    batch_size: int = 16,
) -> None:
    """Fine-tune microsoft/codebert-base for bug-inducing-commit classification.

    Args:
        train_data_path: Path to the curated training dataset (NOT the full 100k+ ApacheJIT).
        checkpoint_dir: Directory to save/resume checkpoints (mount Google Drive on Colab).
        num_epochs: Number of fine-tuning epochs.
        batch_size: Per-device batch size.

    Raises:
        NotImplementedError: Always — not yet implemented.
    """
    raise NotImplementedError("fine_tune_codebert() — see PLANNING.md Week 2.")


def predict_codebert(features: CommitFeatures) -> float:
    """Return CodeBERT's bug-inducing probability for one commit.

    Args:
        features: Structured commit features (never the raw diff string).

    Returns:
        Probability in [0.0, 1.0].

    Raises:
        NotImplementedError: Always — not yet implemented.
    """
    raise NotImplementedError("predict_codebert() — see PLANNING.md Week 2.")
