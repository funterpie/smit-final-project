"""scripts/download_codebert.py — Download fine-tuned CodeBERT from Google Drive.

Usage:
    python scripts/download_codebert.py --drive-folder-id <YOUR_FOLDER_ID>

The script downloads a Google Drive folder (or zip) into
    models/artefacts/codebert/best_model/

Requires gdown:
    pip install gdown
"""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).parent.parent
DEST = ROOT / "models" / "artefacts" / "codebert" / "best_model"


def download(folder_id: str) -> None:
    try:
        import gdown  # type: ignore
    except ImportError:
        print(
            "[download_codebert] ERROR: gdown is not installed.\n"
            "  Run: pip install gdown\n"
            "  Then retry: python scripts/download_codebert.py --drive-folder-id <ID>"
        )
        sys.exit(1)

    DEST.mkdir(parents=True, exist_ok=True)

    # Try folder download first (outputs into a directory named by the folder)
    url = f"https://drive.google.com/drive/folders/{folder_id}"
    print(f"[download_codebert] Downloading from: {url}")
    print(f"[download_codebert] Destination: {DEST}")

    # gdown can download a folder to a local directory
    gdown.download_folder(url, output=str(DEST), quiet=False, use_cookies=False)

    # If the output ended up nested (gdown sometimes creates a subfolder), flatten it
    nested = [p for p in DEST.iterdir() if p.is_dir()]
    if nested and not (DEST / "config.json").exists():
        subfolder = nested[0]
        for f in subfolder.iterdir():
            f.rename(DEST / f.name)
        subfolder.rmdir()
        print(f"[download_codebert] Flattened nested folder: {subfolder.name}")

    # Verify expected files
    required = ["config.json", "tokenizer_config.json"]
    missing = [r for r in required if not (DEST / r).exists()]
    if missing:
        print(f"[download_codebert] WARNING: Missing expected files: {missing}")
        print(f"[download_codebert] Contents of {DEST}:")
        for f in DEST.iterdir():
            print(f"  {f.name}")
    else:
        print(f"[download_codebert] ✓ Model ready at {DEST}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Download CodeBERT checkpoint from Google Drive.")
    parser.add_argument("--drive-folder-id", required=True, help="Google Drive folder ID.")
    args = parser.parse_args()
    download(args.drive_folder_id)


if __name__ == "__main__":
    main()
