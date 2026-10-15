"""models/baseline.py — Logistic regression + random forest baseline.

Training:
    python -m models.baseline --train

Inference:
    from models.baseline import predict_baseline
"""

from __future__ import annotations

import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import MODELS_DIR
from features.schema import CommitFeatures

FEATURE_COLS = [
    "lines_added", "lines_removed", "files_touched", "dispersion",
    "author_bug_rate", "hours_since_last_commit", "tests_added",
    "touches_sensitive_module",
]

_LR_MODEL_PATH = MODELS_DIR / "lr_baseline.pkl"
_RF_MODEL_PATH = MODELS_DIR / "rf_baseline.pkl"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _features_to_array(features: CommitFeatures) -> pd.DataFrame:
    """Convert CommitFeatures to a 1-row DataFrame with named columns."""
    return pd.DataFrame([[
        features.lines_added,
        features.lines_removed,
        features.files_touched,
        features.dispersion,
        features.author_bug_rate,
        features.hours_since_last_commit,
        int(features.tests_added),
        int(features.touches_sensitive_module),
    ]], columns=FEATURE_COLS)


def _load_data(train_csv: str, test_csv: str) -> tuple[
    pd.DataFrame, pd.Series, pd.DataFrame, pd.Series
]:
    train = pd.read_csv(train_csv)
    test = pd.read_csv(test_csv)
    X_train = train[FEATURE_COLS].fillna(0)
    y_train = train["buggy"]
    X_test = test[FEATURE_COLS].fillna(0)
    y_test = test["buggy"]
    return X_train, y_train, X_test, y_test


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def train_baseline(
    train_csv: str,
    test_csv: str,
    output_dir: str | None = None,
) -> dict[str, float]:
    """Train logistic regression and random forest baselines.

    Args:
        train_csv: Path to the processed training CSV (output of prepare_dataset.py).
        test_csv:  Path to the processed test CSV.
        output_dir: Directory to save pickled models. Defaults to config.MODELS_DIR.

    Returns:
        Dict with AUC-ROC and AUC-PR for both models.
    """
    out_dir = Path(output_dir) if output_dir else MODELS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    X_train, y_train, X_test, y_test = _load_data(train_csv, test_csv)
    print(f"[baseline] Train size: {len(X_train):,}  |  Test size: {len(X_test):,}")
    print(f"[baseline] Positive rate (train): {y_train.mean():.3f}")

    # --- Logistic Regression ---
    lr_pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)),
    ])
    lr_pipe.fit(X_train, y_train)
    lr_proba = lr_pipe.predict_proba(X_test)[:, 1]
    lr_aucroc = roc_auc_score(y_test, lr_proba)
    lr_aucpr = average_precision_score(y_test, lr_proba)
    print(f"[baseline][LR]  AUC-ROC={lr_aucroc:.4f}  AUC-PR={lr_aucpr:.4f}")

    with (_LR_MODEL_PATH).open("wb") as fh:
        pickle.dump(lr_pipe, fh)
    print(f"[baseline] Saved LR model → {_LR_MODEL_PATH}")

    # --- Random Forest ---
    rf_pipe = Pipeline([
        ("clf", RandomForestClassifier(
            n_estimators=300, max_depth=None, class_weight="balanced",
            n_jobs=-1, random_state=42,
        )),
    ])
    rf_pipe.fit(X_train, y_train)
    rf_proba = rf_pipe.predict_proba(X_test)[:, 1]
    rf_aucroc = roc_auc_score(y_test, rf_proba)
    rf_aucpr = average_precision_score(y_test, rf_proba)
    print(f"[baseline][RF]  AUC-ROC={rf_aucroc:.4f}  AUC-PR={rf_aucpr:.4f}")

    with (_RF_MODEL_PATH).open("wb") as fh:
        pickle.dump(rf_pipe, fh)
    print(f"[baseline] Saved RF model → {_RF_MODEL_PATH}")

    return {
        "lr_auc_roc": lr_aucroc,
        "lr_auc_pr": lr_aucpr,
        "rf_auc_roc": rf_aucroc,
        "rf_auc_pr": rf_aucpr,
    }


def predict_baseline(features: CommitFeatures, model: str = "rf") -> float:
    """Return baseline model's bug-inducing probability for one commit.

    Args:
        features: Structured commit features.
        model: Which model to use — 'lr' (logistic regression) or 'rf' (random forest).

    Returns:
        Probability in [0.0, 1.0] that the commit is bug-inducing.

    Raises:
        FileNotFoundError: If the model file does not exist (run train_baseline first).
    """
    model_path = _LR_MODEL_PATH if model == "lr" else _RF_MODEL_PATH
    if not model_path.exists():
        raise FileNotFoundError(
            f"Baseline model not found at {model_path}. "
            "Run `python scripts/train_baseline.py` first."
        )

    with model_path.open("rb") as fh:
        pipe: Pipeline = pickle.load(fh)

    X = _features_to_array(features)
    prob: float = pipe.predict_proba(X)[0, 1]
    return float(prob)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    DATA_PROCESSED = Path(__file__).parent.parent / "data" / "processed"

    parser = argparse.ArgumentParser(description="Train baseline models.")
    parser.add_argument("--train-csv", default=str(DATA_PROCESSED / "train_features.csv"))
    parser.add_argument("--test-csv", default=str(DATA_PROCESSED / "test_features.csv"))
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    results = train_baseline(args.train_csv, args.test_csv, args.output_dir)
    print("\n[baseline] Final metrics:", results)
