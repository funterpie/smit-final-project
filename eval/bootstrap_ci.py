"""eval/bootstrap_ci.py — Bootstrap 95% CIs for AUC-PR and Recall@20%.

Usage:
    python eval/bootstrap_ci.py --test-csv data/processed/test_features.csv [--codebert]

Outputs:
    - Updated eval/results.json with CI bounds
    - Console table
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt
import pandas as pd
from sklearn.metrics import average_precision_score

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

N_BOOTSTRAP = 1000
RANDOM_SEED = 42


def recall_at_k_percent(
    y_true: npt.NDArray[Any], y_score: npt.NDArray[Any], k: float = 0.20
) -> float:
    """Fraction of true bugs caught in the top-k% highest-scored commits."""
    n = len(y_true)
    n_top = max(1, int(n * k))
    top_idx = np.argsort(y_score)[::-1][:n_top]
    bugs_caught = y_true[top_idx].sum()
    total_bugs = y_true.sum()
    return float(bugs_caught / total_bugs) if total_bugs > 0 else 0.0


def bootstrap_ci(
    y_true: npt.NDArray[Any],
    y_score: npt.NDArray[Any],
    metric_fn: Any,
    n_resamples: int = N_BOOTSTRAP,
    seed: int = RANDOM_SEED,
    alpha: float = 0.05,
) -> tuple[float, float, float]:
    """Compute bootstrap 95% CI for a given metric function.

    Args:
        y_true: Ground truth labels.
        y_score: Predicted scores/probabilities.
        metric_fn: Function(y_true, y_score) -> float.
        n_resamples: Number of bootstrap resamples.
        seed: Random seed.
        alpha: Significance level (0.05 = 95% CI).

    Returns:
        (point_estimate, lower_bound, upper_bound)
    """
    rng = np.random.RandomState(seed)
    n = len(y_true)
    point_estimate = metric_fn(y_true, y_score)

    boot_values: list[float] = []
    for _ in range(n_resamples):
        idx = rng.randint(0, n, size=n)
        y_t = y_true[idx]
        y_s = y_score[idx]
        # Skip degenerate resamples (all same label)
        if y_t.sum() == 0 or y_t.sum() == n:
            continue
        boot_values.append(metric_fn(y_t, y_s))

    boot_arr = np.array(boot_values)
    lower = float(np.percentile(boot_arr, 100 * alpha / 2))
    upper = float(np.percentile(boot_arr, 100 * (1 - alpha / 2)))
    return point_estimate, lower, upper


def _row_to_features(row: pd.Series) -> CommitFeatures:
    """Convert a DataFrame row to CommitFeatures."""
    return CommitFeatures(
        lines_added=int(row["lines_added"]),
        lines_removed=int(row["lines_removed"]),
        files_touched=int(row["files_touched"]),
        dispersion=float(row["dispersion"]),
        author_bug_rate=float(row["author_bug_rate"]),
        hours_since_last_commit=float(row["hours_since_last_commit"]),
        tests_added=bool(row["tests_added"]),
        touches_sensitive_module=bool(row["touches_sensitive_module"]),
    )


def _get_all_scores(
    df: pd.DataFrame, use_codebert: bool = False
) -> dict[str, npt.NDArray[Any]]:
    """Pre-compute all model scores for every row in df."""
    scores: dict[str, list[float]] = {
        "heuristic": [],
        "baseline_lr": [],
        "baseline_rf": [],
    }
    if use_codebert:
        scores["codebert"] = []

    # Import codebert predictor once if needed
    predict_cb = None
    if use_codebert:
        try:
            from models.codebert import predict_codebert
            predict_cb = predict_codebert
        except (ImportError, FileNotFoundError) as e:
            print(f"[bootstrap] CodeBERT not available: {e}")
            del scores["codebert"]

    print(f"[bootstrap] Scoring {len(df)} commits...")
    for i, (_, row) in enumerate(df.iterrows()):
        feat = _row_to_features(row)
        report = compute_risk(feat)
        scores["heuristic"].append(report.score / 100.0)

        try:
            scores["baseline_lr"].append(predict_baseline(feat, model="lr"))
        except FileNotFoundError:
            scores["baseline_lr"].append(0.0)

        try:
            scores["baseline_rf"].append(predict_baseline(feat, model="rf"))
        except FileNotFoundError:
            scores["baseline_rf"].append(0.0)

        if predict_cb is not None and "codebert" in scores:
            try:
                scores["codebert"].append(predict_cb(feat))
            except Exception:
                scores["codebert"].append(0.0)

        if (i + 1) % 200 == 0:
            print(f"  ... scored {i + 1}/{len(df)}")

    return {k: np.array(v) for k, v in scores.items()}


def run_bootstrap(
    test_csv: str,
    use_codebert: bool = False,
    output_json: str | None = None,
) -> dict[str, Any]:
    """Run bootstrap CI evaluation for all models.

    Returns:
        Dict with results including CIs.
    """
    df = pd.read_csv(test_csv).fillna(0)
    y_true = df["buggy"].values
    print(f"[bootstrap] Test set: {len(df):,} commits  |  Positive rate: {y_true.mean():.3f}")

    all_scores = _get_all_scores(df, use_codebert=use_codebert)
    results: dict[str, Any] = {}

    model_names = {"heuristic": "Heuristic", "baseline_lr": "LR", "baseline_rf": "RF", "codebert": "CodeBERT"}

    for key in all_scores:
        y_score = all_scores[key]
        name = model_names.get(key, key)

        print(f"\n[bootstrap] Computing CIs for {name} ({N_BOOTSTRAP} resamples)...")

        auc_pr_pt, auc_pr_lo, auc_pr_hi = bootstrap_ci(
            y_true, y_score, average_precision_score
        )
        r20_pt, r20_lo, r20_hi = bootstrap_ci(
            y_true, y_score, lambda yt, ys: recall_at_k_percent(yt, ys, 0.20)
        )

        results[key] = {
            "auc_pr": round(auc_pr_pt, 4),
            "auc_pr_ci_lower": round(auc_pr_lo, 4),
            "auc_pr_ci_upper": round(auc_pr_hi, 4),
            "recall_at_20pct": round(r20_pt, 4),
            "recall_at_20pct_ci_lower": round(r20_lo, 4),
            "recall_at_20pct_ci_upper": round(r20_hi, 4),
        }

        print(
            f"  AUC-PR:       {auc_pr_pt:.4f}  [{auc_pr_lo:.4f}, {auc_pr_hi:.4f}]"
        )
        print(
            f"  Recall@20%:   {r20_pt:.4f}  [{r20_lo:.4f}, {r20_hi:.4f}]"
        )

    # Summary table
    print("\n" + "=" * 75)
    print(f"{'Model':<12}  {'AUC-PR':>8}  {'95% CI':>18}  {'Rec@20%':>8}  {'95% CI':>18}")
    print("-" * 75)
    for key in all_scores:
        r = results[key]
        name = model_names.get(key, key)
        print(
            f"{name:<12}  {r['auc_pr']:8.4f}  "
            f"[{r['auc_pr_ci_lower']:.4f}, {r['auc_pr_ci_upper']:.4f}]  "
            f"{r['recall_at_20pct']:8.4f}  "
            f"[{r['recall_at_20pct_ci_lower']:.4f}, {r['recall_at_20pct_ci_upper']:.4f}]"
        )
    print("=" * 75)

    # Check if CodeBERT vs RF difference is significant (non-overlapping CIs)
    if "baseline_rf" in results and "codebert" in results:
        rf_r = results["baseline_rf"]
        cb_r = results["codebert"]
        overlap_auc = rf_r["auc_pr_ci_upper"] >= cb_r["auc_pr_ci_lower"] and \
                      cb_r["auc_pr_ci_upper"] >= rf_r["auc_pr_ci_lower"]
        overlap_r20 = rf_r["recall_at_20pct_ci_upper"] >= cb_r["recall_at_20pct_ci_lower"] and \
                      cb_r["recall_at_20pct_ci_upper"] >= rf_r["recall_at_20pct_ci_lower"]

        print("\n[bootstrap] CodeBERT vs RF comparison:")
        delta_auc = cb_r["auc_pr"] - rf_r["auc_pr"]
        delta_r20 = cb_r["recall_at_20pct"] - rf_r["recall_at_20pct"]
        print(f"  AUC-PR delta:     {delta_auc:+.4f}  CIs overlap: {'YES' if overlap_auc else 'NO'}")
        print(f"  Recall@20% delta: {delta_r20:+.4f}  CIs overlap: {'YES' if overlap_r20 else 'NO'}")
        if overlap_auc:
            print("  → AUC-PR improvement is NOT statistically significant at 95% level")
        else:
            print("  → AUC-PR improvement IS statistically significant at 95% level")
        if overlap_r20:
            print("  → Recall@20% improvement is NOT statistically significant at 95% level")
        else:
            print("  → Recall@20% improvement IS statistically significant at 95% level")

    # Save results
    out_path = Path(output_json) if output_json else Path(__file__).parent / "results.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Merge with existing results to preserve other fields (auc_roc, fpr)
    existing: dict[str, Any] = {}
    if out_path.exists():
        with out_path.open() as fh:
            existing = json.load(fh)

    for key in results:
        if key in existing:
            existing[key].update(results[key])
        else:
            existing[key] = results[key]

    with out_path.open("w") as fh:
        json.dump(existing, fh, indent=2)
    print(f"\n[bootstrap] Results saved → {out_path}")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bootstrap 95% CIs for evaluation metrics.")
    parser.add_argument("--test-csv", required=True, help="Path to processed test CSV.")
    parser.add_argument("--output-json", default=None, help="Path to write results JSON.")
    parser.add_argument("--codebert", action="store_true", help="Also evaluate CodeBERT model.")
    args = parser.parse_args()
    run_bootstrap(args.test_csv, args.codebert, args.output_json)
