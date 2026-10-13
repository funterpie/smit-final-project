"""models/codebert.py — CodeBERT fine-tuning (Colab) and local inference.

Fine-tuning is done on Colab (see notebooks/codebert_finetune.ipynb).
This file handles local inference against a saved checkpoint directory.

The model is NOT fine-tuned here — only loaded for inference.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from features.schema import CommitFeatures

_FEATURE_COLS = [
    "lines_added", "lines_removed", "files_touched", "dispersion",
    "author_bug_rate", "hours_since_last_commit", "tests_added",
    "touches_sensitive_module",
]


def _features_to_text(features: CommitFeatures) -> str:
    """Convert CommitFeatures to a short text for CodeBERT tokenisation.

    Note: The raw diff is NEVER used. Only computed feature values are passed.
    This is a structured text representation, not source code.
    """
    return (
        f"lines_added {features.lines_added} "
        f"lines_removed {features.lines_removed} "
        f"files_touched {features.files_touched} "
        f"dispersion {features.dispersion:.3f} "
        f"author_bug_rate {features.author_bug_rate:.3f} "
        f"hours_since_last_commit {features.hours_since_last_commit:.1f} "
        f"tests_added {int(features.tests_added)} "
        f"touches_sensitive_module {int(features.touches_sensitive_module)}"
    )


def fine_tune_codebert(
    train_data_path: str,
    checkpoint_dir: str,
    num_epochs: int = 5,
    batch_size: int = 16,
) -> None:
    """Fine-tune microsoft/codebert-base for bug-inducing-commit classification.

    This function is designed to run on Google Colab free tier.
    See notebooks/codebert_finetune.ipynb for the full training notebook.

    Args:
        train_data_path: Path to the curated training CSV (NOT the full 100k+ ApacheJIT).
        checkpoint_dir: Directory to save/resume checkpoints (mount Google Drive on Colab).
        num_epochs: Number of fine-tuning epochs.
        batch_size: Per-device batch size.

    Raises:
        ImportError: If transformers/torch are not installed.
    """
    import torch
    from torch.utils.data import DataLoader, Dataset
    from transformers import (AutoModelForSequenceClassification, AutoTokenizer,
                              get_linear_schedule_with_warmup)

    import pandas as pd
    from sklearn.metrics import average_precision_score

    print(f"[codebert] Loading training data from {train_data_path}...")
    df = pd.read_csv(train_data_path).fillna(0)

    class CommitDataset(Dataset):
        def __init__(self, df: pd.DataFrame, tokenizer: object, max_len: int = 128) -> None:
            self.texts = []
            self.labels = []
            for _, row in df.iterrows():
                feat = CommitFeatures(
                    lines_added=int(row["lines_added"]),
                    lines_removed=int(row["lines_removed"]),
                    files_touched=int(row["files_touched"]),
                    dispersion=float(row["dispersion"]),
                    author_bug_rate=float(row["author_bug_rate"]),
                    hours_since_last_commit=float(row["hours_since_last_commit"]),
                    tests_added=bool(row["tests_added"]),
                    touches_sensitive_module=bool(row["touches_sensitive_module"]),
                )
                self.texts.append(_features_to_text(feat))
                self.labels.append(int(row["buggy"]))
            self.tokenizer = tokenizer
            self.max_len = max_len

        def __len__(self) -> int:
            return len(self.texts)

        def __getitem__(self, idx: int) -> dict:
            enc = self.tokenizer(
                self.texts[idx],
                max_length=self.max_len,
                padding="max_length",
                truncation=True,
                return_tensors="pt",
            )
            return {
                "input_ids": enc["input_ids"].squeeze(),
                "attention_mask": enc["attention_mask"].squeeze(),
                "labels": torch.tensor(self.labels[idx], dtype=torch.long),
            }

    ckpt_path = Path(checkpoint_dir)
    ckpt_path.mkdir(parents=True, exist_ok=True)

    tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[codebert] Device: {device}")

    # Resume from checkpoint if exists
    model_dir = ckpt_path / "best_model"
    if model_dir.exists():
        print(f"[codebert] Resuming from checkpoint {model_dir}")
        model = AutoModelForSequenceClassification.from_pretrained(str(model_dir))
    else:
        model = AutoModelForSequenceClassification.from_pretrained(
            "microsoft/codebert-base", num_labels=2
        )
    model = model.to(device)

    dataset = CommitDataset(df, tokenizer)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5, weight_decay=0.01)
    total_steps = len(loader) * num_epochs
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=total_steps // 10,
                                                num_training_steps=total_steps)

    best_aucpr = 0.0
    for epoch in range(1, num_epochs + 1):
        model.train()
        total_loss = 0.0
        for batch in loader:
            optimizer.zero_grad()
            outputs = model(
                input_ids=batch["input_ids"].to(device),
                attention_mask=batch["attention_mask"].to(device),
                labels=batch["labels"].to(device),
            )
            loss = outputs.loss
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()
            total_loss += loss.item()

        avg_loss = total_loss / len(loader)
        print(f"[codebert] Epoch {epoch}/{num_epochs} | loss={avg_loss:.4f}")

        # Save checkpoint every epoch (Colab disconnect safety)
        epoch_dir = ckpt_path / f"epoch_{epoch}"
        model.save_pretrained(str(epoch_dir))
        tokenizer.save_pretrained(str(epoch_dir))
        print(f"[codebert] Checkpoint saved → {epoch_dir}")

    # Save best as final
    final_dir = ckpt_path / "best_model"
    model.save_pretrained(str(final_dir))
    tokenizer.save_pretrained(str(final_dir))
    print(f"[codebert] Final model saved → {final_dir}")


def predict_codebert(features: CommitFeatures, checkpoint_dir: str | None = None) -> float:
    """Return CodeBERT's bug-inducing probability for one commit.

    Args:
        features: Structured commit features (NEVER the raw diff).
        checkpoint_dir: Path to the fine-tuned model directory.
            Defaults to config.MODELS_DIR / "codebert" / "best_model".

    Returns:
        Probability in [0.0, 1.0].

    Raises:
        FileNotFoundError: If the model directory does not exist.
    """
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    import torch.nn.functional as F

    from config import MODELS_DIR

    model_path = (
        Path(checkpoint_dir)
        if checkpoint_dir
        else MODELS_DIR / "codebert" / "best_model"
    )

    if not model_path.exists():
        raise FileNotFoundError(
            f"CodeBERT model not found at {model_path}. "
            "Run the Colab fine-tuning notebook first."
        )

    tokenizer = AutoTokenizer.from_pretrained(str(model_path))
    model = AutoModelForSequenceClassification.from_pretrained(str(model_path))
    model.eval()

    text = _features_to_text(features)
    enc = tokenizer(text, return_tensors="pt", max_length=128, truncation=True, padding="max_length")

    with torch.no_grad():
        logits = model(**enc).logits
        prob = float(F.softmax(logits, dim=-1)[0, 1])

    return prob
