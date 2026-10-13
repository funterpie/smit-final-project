"""scripts/train_baseline.py — Quick entry point to train baseline models.

Usage:
    python scripts/train_baseline.py
    python scripts/train_baseline.py --sample 5000  # fast demo

Runs prepare_dataset.py (if processed CSVs not yet present), then trains
LR + RF models and saves them to models/artefacts/.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

DATA_PROCESSED = Path(__file__).parent.parent / "data" / "processed"
TRAIN_CSV = DATA_PROCESSED / "train_features.csv"
TEST_CSV = DATA_PROCESSED / "test_features.csv"


def main(sample: int = 0) -> None:
    # Step 1: Prepare dataset if not already done
    if not TRAIN_CSV.exists() or not TEST_CSV.exists():
        print("[train_baseline] Processed data not found — running prepare_dataset.py first...")
        from scripts.prepare_dataset import main as prepare
        prepare(sample=sample)
    else:
        print(f"[train_baseline] Using existing processed data: {TRAIN_CSV}")

    # Step 2: Train baseline models
    from models.baseline import train_baseline
    results = train_baseline(str(TRAIN_CSV), str(TEST_CSV))

    print("\n" + "=" * 60)
    print("BASELINE RESULTS")
    print("=" * 60)
    for model, metrics in results.items() if isinstance(results, dict) else []:
        pass
    for key, val in results.items():
        print(f"  {key:<20} {val:.4f}")
    print("=" * 60)
    print("Models saved to models/artefacts/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", type=int, default=0,
                        help="Sample N rows from dataset (0 = use all). Use 5000 for speed demo.")
    args = parser.parse_args()
    main(sample=args.sample)
