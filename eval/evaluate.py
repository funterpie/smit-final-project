"""eval/evaluate.py — AUC-PR, recall@20%, false-positive rate, explanation quality.

Usage:
    python eval/evaluate.py --test-csv data/processed/test_features.csv

Outputs:
    - Console table with metrics
    - eval/results.json (for report)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    roc_auc_score,
    precision_recall_curve,
)

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import MODELS_DIR
from features.schema import CommitFeatures
from models.baseline import predict_baseline
from models.risk_engine import compute_risk

FEATURE_COLS = [
    "lines_added", "lines_removed", "files_touched", "dispersion",
    "author_bug_rate", "hours_since_last_commit", "tests_added",
    "touches_sensitive_module",
]


def recall_at_k_percent(y_true: np.ndarray, y_score: np.ndarray, k: float = 0.20) -> float:
    """What fraction of true bugs are caught in the top-k% highest-scored commits?"""
    n = len(y_true)
    n_top = max(1, int(n * k))
    top_idx = np.argsort(y_score)[::-1][:n_top]
    bugs_caught = y_true[top_idx].sum()
    total_bugs = y_true.sum()
    return float(bugs_caught / total_bugs) if total_bugs > 0 else 0.0


def false_positive_rate_at_threshold(
    y_true: np.ndarray, y_score: np.ndarray, threshold: float = 0.5
) -> float:
    """FPR = FP / (FP + TN) at a given score threshold."""
    preds = (y_score >= threshold).astype(int)
    fp = ((preds == 1) & (y_true == 0)).sum()
    tn = ((preds == 0) & (y_true == 0)).sum()
    return float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0


def evaluate(
    test_csv: str,
    output_json: str | None = None,
    use_codebert: bool = False,
) -> dict[str, float | dict]:
    """Run full evaluation on test set.

    Args:
        test_csv: Path to processed test CSV.
        output_json: Where to write results JSON. Defaults to eval/results.json.
        use_codebert: Whether to also evaluate CodeBERT model.

    Returns:
        Dict with all metric values.
    """
    df = pd.read_csv(test_csv).fillna(0)
    y_true = df["buggy"].values

    print(f"[eval] Test set: {len(df):,} commits  |  Positive rate: {y_true.mean():.3f}")

    results: dict = {}

    # ---- Heuristic risk engine (no ML) ----
    heuristic_scores = []
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
        report = compute_risk(feat)
        heuristic_scores.append(report.score / 100.0)

    h_scores = np.array(heuristic_scores)
    results["heuristic"] = {
        "auc_roc": round(roc_auc_score(y_true, h_scores), 4),
        "auc_pr": round(average_precision_score(y_true, h_scores), 4),
        "recall_at_20pct": round(recall_at_k_percent(y_true, h_scores, 0.20), 4),
        "fpr_at_0.5": round(false_positive_rate_at_threshold(y_true, h_scores, 0.5), 4),
    }
    print(f"[eval][Heuristic]  {results['heuristic']}")

    # ---- Logistic Regression baseline ----
    try:
        lr_probs = []
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
            lr_probs.append(predict_baseline(feat, model="lr"))
        lr_arr = np.array(lr_probs)
        results["baseline_lr"] = {
            "auc_roc": round(roc_auc_score(y_true, lr_arr), 4),
            "auc_pr": round(average_precision_score(y_true, lr_arr), 4),
            "recall_at_20pct": round(recall_at_k_percent(y_true, lr_arr, 0.20), 4),
            "fpr_at_0.5": round(false_positive_rate_at_threshold(y_true, lr_arr, 0.5), 4),
        }
        print(f"[eval][LR Baseline] {results['baseline_lr']}")
    except FileNotFoundError as e:
        print(f"[eval] LR model not found: {e}")

    # ---- Random Forest baseline ----
    try:
        rf_probs = []
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
            rf_probs.append(predict_baseline(feat, model="rf"))
        rf_arr = np.array(rf_probs)
        results["baseline_rf"] = {
            "auc_roc": round(roc_auc_score(y_true, rf_arr), 4),
            "auc_pr": round(average_precision_score(y_true, rf_arr), 4),
            "recall_at_20pct": round(recall_at_k_percent(y_true, rf_arr, 0.20), 4),
            "fpr_at_0.5": round(false_positive_rate_at_threshold(y_true, rf_arr, 0.5), 4),
        }
        print(f"[eval][RF Baseline] {results['baseline_rf']}")
    except FileNotFoundError as e:
        print(f"[eval] RF model not found: {e}")

    # ---- CodeBERT (optional) ----
    if use_codebert:
        try:
            from models.codebert import predict_codebert
            cb_probs = []
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
                cb_probs.append(predict_codebert(feat))
            cb_arr = np.array(cb_probs)
            results["codebert"] = {
                "auc_roc": round(roc_auc_score(y_true, cb_arr), 4),
                "auc_pr": round(average_precision_score(y_true, cb_arr), 4),
                "recall_at_20pct": round(recall_at_k_percent(y_true, cb_arr, 0.20), 4),
                "fpr_at_0.5": round(false_positive_rate_at_threshold(y_true, cb_arr, 0.5), 4),
            }
            print(f"[eval][CodeBERT] {results['codebert']}")
        except (FileNotFoundError, ImportError) as e:
            print(f"[eval] CodeBERT not available: {e}")

    # Save results
    out_path = Path(output_json) if output_json else Path(__file__).parent / "results.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w") as fh:
        json.dump(results, fh, indent=2)
    print(f"[eval] Results saved → {out_path}")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate all models on the test set.")
    parser.add_argument("--test-csv", required=True, help="Path to processed test CSV.")
    parser.add_argument("--output-json", default=None, help="Path to write results JSON.")
    parser.add_argument("--codebert", action="store_true", help="Also evaluate CodeBERT.")
    args = parser.parse_args()
    evaluate(args.test_csv, args.output_json, args.codebert)
