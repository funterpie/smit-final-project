"""features/extract.py — PyDriller-based diff feature extraction.

Extracts CommitFeatures from a live git repository using PyDriller.
Also provides a helper to map an ApacheJIT CSV row to CommitFeatures
for offline training (no live repo needed).
"""

from __future__ import annotations

import math
from collections import Counter
from pathlib import Path
from typing import Optional

from pydriller import Repository

from features.schema import CommitFeatures

# Files that touch security-critical modules (heuristic list)
_SENSITIVE_PATTERNS = {
    "auth", "crypto", "security", "payment", "passwd", "secret",
    "credential", "token", "ssl", "tls", "cipher", "encrypt", "login",
}


def _is_sensitive(filepath: str) -> bool:
    """Return True if any part of the filepath matches a sensitive pattern."""
    parts = Path(filepath).parts
    return any(
        any(pattern in part.lower() for pattern in _SENSITIVE_PATTERNS)
        for part in parts
    )


def _path_dispersion(modified_files: list[str]) -> float:
    """
    Compute a simple path-entropy dispersion score.

    High value (~>3) means changes are spread across many directories (cross-cutting).
    Uses Shannon entropy over the top-level directory distribution.
    """
    if not modified_files:
        return 0.0
    dirs = [str(Path(f).parts[0]) if len(Path(f).parts) > 1 else "_root"
            for f in modified_files]
    counts = Counter(dirs)
    total = sum(counts.values())
    entropy = -sum((c / total) * math.log2(c / total) for c in counts.values() if c > 0)
    # Scale: entropy of N uniform dirs = log2(N). Normalise to a 0-10ish range.
    return round(entropy * len(counts), 3)


def extract_features(repo_path: str, commit_hash: str) -> CommitFeatures:
    """Extract risk-relevant features from a single commit using PyDriller.

    Args:
        repo_path: Absolute or relative path to the local git repository.
        commit_hash: Full or short SHA of the commit to analyse.

    Returns:
        A populated CommitFeatures instance.

    Raises:
        ValueError: If the commit is not found in the repository.
    """
    repo_path = str(Path(repo_path).resolve())

    commits = list(Repository(repo_path, single=commit_hash).traverse_commits())
    if not commits:
        raise ValueError(f"Commit '{commit_hash}' not found in repo '{repo_path}'.")

    commit = commits[0]
    modified_paths = [mf.new_path or mf.old_path or "" for mf in commit.modified_files]
    modified_paths = [p for p in modified_paths if p]

    lines_added = sum(
        mf.added_lines for mf in commit.modified_files if mf.added_lines
    )
    lines_removed = sum(
        mf.deleted_lines for mf in commit.modified_files if mf.deleted_lines
    )
    files_touched = len(commit.modified_files)
    dispersion = _path_dispersion(modified_paths)

    tests_added = any(
        "test" in (mf.new_path or "").lower() or "test" in (mf.old_path or "").lower()
        for mf in commit.modified_files
    )
    touches_sensitive_module = any(_is_sensitive(p) for p in modified_paths)

    # Author bug rate: we can't compute this from a single commit; callers should supply it.
    # When called from CLI with no prior stats, we default to 0.0 (unknown).
    author_bug_rate: float = 0.0

    # hours_since_last_commit: use commit's own author_date vs prev commit
    hours_since_last_commit: float = 0.0
    prev_commits = list(
        Repository(repo_path, to_commit=commit_hash).traverse_commits()
    )
    if len(prev_commits) >= 2:
        current_dt = prev_commits[-1].author_date
        prev_dt = prev_commits[-2].author_date
        delta = current_dt - prev_dt
        hours_since_last_commit = round(delta.total_seconds() / 3600, 2)

    return CommitFeatures(
        lines_added=lines_added,
        lines_removed=lines_removed,
        files_touched=files_touched,
        dispersion=dispersion,
        author_bug_rate=author_bug_rate,
        hours_since_last_commit=max(0.0, hours_since_last_commit),
        tests_added=tests_added,
        touches_sensitive_module=touches_sensitive_module,
    )


def features_from_apachejit_row(row: dict) -> CommitFeatures:
    """Map an ApacheJIT CSV row dict to CommitFeatures.

    ApacheJIT columns used:
        la    → lines_added
        ld    → lines_removed
        nf    → files_touched
        ent   → dispersion (Shannon entropy of file-path distribution)
        arexp → author_bug_rate (normalised to [0,1] if > 1, else as-is)
        age   → hours_since_last_commit (age in months → hours approximation)

    Notes:
        - tests_added and touches_sensitive_module cannot be derived from
          ApacheJIT features alone; they default to False for training purposes.
    """
    arexp: float = float(row.get("arexp") or 0.0)
    # arexp is a cumulative count in some dataset versions — cap to [0, 1]
    author_bug_rate = min(arexp / max(float(row.get("aexp") or 1), 1), 1.0)

    age_months: float = float(row.get("age") or 0.0)
    hours_since_last_commit = age_months * 30 * 24  # rough conversion

    return CommitFeatures(
        lines_added=int(float(row.get("la") or 0)),
        lines_removed=int(float(row.get("ld") or 0)),
        files_touched=int(float(row.get("nf") or 0)),
        dispersion=float(row.get("ent") or 0.0),
        author_bug_rate=round(max(0.0, min(1.0, author_bug_rate)), 4),
        hours_since_last_commit=round(hours_since_last_commit, 2),
        tests_added=False,           # not in ApacheJIT features
        touches_sensitive_module=False,  # not in ApacheJIT features
    )
