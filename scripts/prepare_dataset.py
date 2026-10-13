"""scripts/prepare_dataset.py — Convert ApacheJIT CSV to processed feature CSVs.

Usage:
    python scripts/prepare_dataset.py [--sample 5000] [--seed 42]

Output:
    data/processed/train_features.csv
    data/processed/test_features.csv
    data/processed/bug_inducing_commits.jsonl   (for RAG index)

Steps:
1. Load apachejit_total.csv (or apachejit_train.csv / apachejit_test.csv)
2. Map each row to CommitFeatures fields using features_from_apachejit_row()
3. Save train/test splits with binary `buggy` label
4. Export bug-inducing commits as JSONL for RAG embedding
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

# Allow running as a top-level script
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from sklearn.model_selection import train_test_split

from features.extract import features_from_apachejit_row

DATA_RAW = Path(__file__).parent.parent / "data" / "raw" / "apachejit_dataset_replication" / "apachejit" / "dataset"
DATA_PROCESSED = Path(__file__).parent.parent / "data" / "processed"

FEATURE_COLS = [
    "lines_added", "lines_removed", "files_touched", "dispersion",
    "author_bug_rate", "hours_since_last_commit", "tests_added",
    "touches_sensitive_module",
]


def main(sample: int = 0, seed: int = 42) -> None:
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

    csv_path = DATA_RAW / "apachejit_total.csv"
    print(f"[prepare_dataset] Loading {csv_path}...")

    df = pd.read_csv(csv_path, low_memory=False)
    print(f"[prepare_dataset] Loaded {len(df):,} rows. Columns: {list(df.columns)}")

    # Parse buggy label
    df["buggy_label"] = df["buggy"].astype(str).str.lower().isin(["true", "1"]).astype(int)

    # Optional sample (stratified by label) — keep class balance
    if sample > 0 and sample < len(df):
        df, _ = train_test_split(df, train_size=sample, stratify=df["buggy_label"], random_state=seed)
        print(f"[prepare_dataset] Sampled to {len(df):,} rows (stratified).")

    # Map to CommitFeatures
    print("[prepare_dataset] Extracting features from dataset rows...")
    rows: list[dict] = []
    for _, row in df.iterrows():
        feat = features_from_apachejit_row(row.to_dict())
        record = feat.model_dump()
        record["buggy"] = int(row["buggy_label"])
        record["commit_id"] = str(row.get("commit_id", ""))
        record["project"] = str(row.get("project", ""))
        rows.append(record)

    feat_df = pd.DataFrame(rows)
    print(f"[prepare_dataset] Feature columns: {list(feat_df.columns)}")
    print(f"[prepare_dataset] Buggy distribution:\n{feat_df['buggy'].value_counts()}")

    # Train/test split (80/20 stratified)
    train_df, test_df = train_test_split(
        feat_df, test_size=0.20, stratify=feat_df["buggy"], random_state=seed
    )
    print(f"[prepare_dataset] Train: {len(train_df):,}  |  Test: {len(test_df):,}")

    train_path = DATA_PROCESSED / "train_features.csv"
    test_path = DATA_PROCESSED / "test_features.csv"
    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)
    print(f"[prepare_dataset] Saved: {train_path}")
    print(f"[prepare_dataset] Saved: {test_path}")

    # Export bug-inducing commits for RAG
    rag_path = DATA_PROCESSED / "bug_inducing_commits.jsonl"
    bug_df = feat_df[feat_df["buggy"] == 1].copy()
    print(f"[prepare_dataset] Exporting {len(bug_df):,} bug-inducing commits for RAG → {rag_path}")
    with rag_path.open("w") as fh:
        for record in bug_df.to_dict(orient="records"):
            # RAG only needs feature fields + commit metadata, not the label
            rag_record = {k: record[k] for k in FEATURE_COLS + ["commit_id", "project"]}
            rag_record["summary"] = (
                f"{record['project']} | +{record['lines_added']}/-{record['lines_removed']} lines "
                f"| {record['files_touched']} files | dispersion={record['dispersion']:.2f}"
            )
            fh.write(json.dumps(rag_record) + "\n")
    print("[prepare_dataset] Done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare ApacheJIT dataset.")
    parser.add_argument("--sample", type=int, default=0,
                        help="If >0, sample this many rows (stratified). Default: use all.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    args = parser.parse_args()
    main(sample=args.sample, seed=args.seed)
