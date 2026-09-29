"""api/audit.py — SQLite audit log for human reviewer decisions.

Table: decisions
  id            INTEGER PRIMARY KEY AUTOINCREMENT
  timestamp     TEXT    ISO-8601 UTC timestamp
  commit_hash   TEXT    the reviewed commit
  score         INTEGER risk score (0-100)
  explanation   TEXT    LLM-generated explanation (may be empty at scaffold stage)
  decision      TEXT    'approve' | 'request_changes' | 'escalate'
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Generator


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------
_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS decisions (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp    TEXT    NOT NULL,
    commit_hash  TEXT    NOT NULL,
    score        INTEGER NOT NULL,
    explanation  TEXT    NOT NULL DEFAULT '',
    decision     TEXT    NOT NULL CHECK(decision IN ('approve', 'request_changes', 'escalate'))
);
"""

_VALID_DECISIONS = {"approve", "request_changes", "escalate"}


# ---------------------------------------------------------------------------
# Connection helper
# ---------------------------------------------------------------------------
def _connect(db_path: Path) -> sqlite3.Connection:
    """Open (and initialise, if new) a SQLite connection to *db_path*."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute(_CREATE_TABLE_SQL)
    conn.commit()
    return conn


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def insert_decision(
    db_path: Path | str,
    commit_hash: str,
    score: int,
    decision: str,
    explanation: str = "",
) -> int:
    """Insert a reviewer decision into the audit log.

    Args:
        db_path: Path to the SQLite database file.
        commit_hash: The git commit SHA that was reviewed.
        score: Risk score produced by the risk engine (0-100).
        decision: One of 'approve', 'request_changes', or 'escalate'.
        explanation: Optional LLM-generated explanation text.

    Returns:
        The auto-assigned row id.

    Raises:
        ValueError: If *decision* is not one of the valid choices.
    """
    if decision not in _VALID_DECISIONS:
        raise ValueError(
            f"Invalid decision '{decision}'. Must be one of: {sorted(_VALID_DECISIONS)}"
        )

    timestamp = datetime.now(timezone.utc).isoformat()
    conn = _connect(Path(db_path))
    try:
        cursor = conn.execute(
            "INSERT INTO decisions (timestamp, commit_hash, score, explanation, decision) "
            "VALUES (?, ?, ?, ?, ?)",
            (timestamp, commit_hash, score, explanation, decision),
        )
        conn.commit()
        return cursor.lastrowid  # type: ignore[return-value]
    finally:
        conn.close()


def list_decisions(db_path: Path | str) -> list[dict[str, object]]:
    """Return all rows from the decisions table, newest first.

    Args:
        db_path: Path to the SQLite database file.

    Returns:
        A list of dicts with keys: id, timestamp, commit_hash, score,
        explanation, decision.
    """
    conn = _connect(Path(db_path))
    try:
        rows = conn.execute(
            "SELECT * FROM decisions ORDER BY id DESC"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()
