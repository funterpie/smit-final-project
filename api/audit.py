"""api/audit.py — SQLite audit log for reviews and human decisions.

Tables:
  reviews
    id                INTEGER PRIMARY KEY AUTOINCREMENT
    timestamp         TEXT    ISO-8601 UTC
    commit_ref        TEXT    commit hash or ref
    diff_hash         TEXT    SHA-256 of the raw diff (never store the diff itself)
    score             INTEGER risk score 0-100
    signals_json      TEXT    JSON array of signal dicts
    evidence_json     TEXT    JSON (nullable) — RAG evidence
    explanation       TEXT    plain-English explanation
    explanation_source TEXT   'groq' | 'local_fallback'

  decisions
    id            INTEGER PRIMARY KEY AUTOINCREMENT
    review_id     INTEGER FK → reviews.id
    timestamp     TEXT    ISO-8601 UTC
    decision      TEXT    'approve' | 'request_changes' | 'escalate'
    note          TEXT    optional reviewer note
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------
_CREATE_REVIEWS_SQL = """
CREATE TABLE IF NOT EXISTS reviews (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp          TEXT    NOT NULL,
    commit_ref         TEXT    NOT NULL,
    diff_hash          TEXT    NOT NULL DEFAULT '',
    score              INTEGER NOT NULL,
    signals_json       TEXT    NOT NULL DEFAULT '[]',
    evidence_json      TEXT,
    explanation        TEXT    NOT NULL DEFAULT '',
    explanation_source TEXT    NOT NULL DEFAULT 'local_fallback',
    fallback_reason   TEXT
);
"""

_CREATE_DECISIONS_SQL = """
CREATE TABLE IF NOT EXISTS decisions (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    review_id  INTEGER NOT NULL REFERENCES reviews(id),
    timestamp  TEXT    NOT NULL,
    decision   TEXT    NOT NULL CHECK(decision IN ('approve', 'request_changes', 'escalate')),
    note       TEXT    NOT NULL DEFAULT ''
);
"""

# Migrate: old decisions table may exist without review_id
_MIGRATE_OLD_DECISIONS = """
DROP TABLE IF EXISTS decisions_old;
"""

_VALID_DECISIONS = {"approve", "request_changes", "escalate"}


# ---------------------------------------------------------------------------
# Connection helper
# ---------------------------------------------------------------------------
def _connect(db_path: Path) -> sqlite3.Connection:
    """Open (and initialise if new) a SQLite connection."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute(_CREATE_REVIEWS_SQL)
    review_cols = [row["name"] for row in conn.execute("PRAGMA table_info(reviews)").fetchall()]
    if "fallback_reason" not in review_cols:
        conn.execute("ALTER TABLE reviews ADD COLUMN fallback_reason TEXT")
    # Check if old decisions table exists (without review_id) and drop it
    cursor = conn.execute("PRAGMA table_info(decisions)")
    cols = [row["name"] for row in cursor.fetchall()]
    if cols and "review_id" not in cols:
        conn.execute("DROP TABLE IF EXISTS decisions")
    conn.execute(_CREATE_DECISIONS_SQL)
    conn.commit()
    return conn


# ---------------------------------------------------------------------------
# Reviews
# ---------------------------------------------------------------------------
def insert_review(
    db_path: Path | str,
    commit_ref: str,
    diff_hash: str,
    score: int,
    signals: list[dict[str, Any]],
    evidence: dict[str, Any] | None,
    explanation: str,
    explanation_source: str,
    fallback_reason: str | None = None,
) -> int:
    """Insert a review result. Returns the row id."""
    timestamp = datetime.now(timezone.utc).isoformat()
    conn = _connect(Path(db_path))
    try:
        cursor = conn.execute(
            "INSERT INTO reviews "
            "(timestamp, commit_ref, diff_hash, score, signals_json, "
            " evidence_json, explanation, explanation_source, fallback_reason) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                timestamp,
                commit_ref,
                diff_hash,
                score,
                json.dumps(signals),
                json.dumps(evidence) if evidence else None,
                explanation,
                explanation_source,
                fallback_reason,
            ),
        )
        conn.commit()
        return cursor.lastrowid  # type: ignore[return-value]
    finally:
        conn.close()


def list_reviews(
    db_path: Path | str,
    risk: str | None = None,
    decision: str | None = None,
) -> list[dict[str, Any]]:
    """List reviews, optionally filtered. Sorted by score DESC.

    Args:
        risk: 'high' (>=70), 'medium' (30-69), 'low' (<30), or None.
        decision: 'pending', 'approve', 'request_changes', 'escalate', or None.
    """
    conn = _connect(Path(db_path))
    try:
        base = (
            "SELECT r.*, "
            "  (SELECT d.decision FROM decisions d WHERE d.review_id = r.id "
            "   ORDER BY d.id DESC LIMIT 1) AS latest_decision "
            "FROM reviews r "
        )
        conditions: list[str] = []
        params: list[Any] = []

        if risk == "high":
            conditions.append("r.score >= 70")
        elif risk == "medium":
            conditions.append("r.score >= 30 AND r.score < 70")
        elif risk == "low":
            conditions.append("r.score < 30")

        if conditions:
            base += "WHERE " + " AND ".join(conditions) + " "

        base += "ORDER BY r.score DESC"

        rows = conn.execute(base, params).fetchall()
        result = []
        for row in rows:
            d = dict(row)
            d["signals"] = json.loads(d.pop("signals_json", "[]"))
            ej = d.pop("evidence_json", None)
            d["evidence"] = json.loads(ej) if ej else None
            d["decision"] = d.pop("latest_decision", None)
            result.append(d)

        # Client-side filter for decision (needs the subquery result)
        if decision:
            if decision == "pending":
                result = [r for r in result if r["decision"] is None]
            else:
                result = [r for r in result if r["decision"] == decision]

        return result
    finally:
        conn.close()


def get_review(db_path: Path | str, review_id: int) -> dict[str, Any] | None:
    """Get a single review by id, or None."""
    conn = _connect(Path(db_path))
    try:
        row = conn.execute("SELECT * FROM reviews WHERE id = ?", (review_id,)).fetchone()
        if row is None:
            return None
        d = dict(row)
        d["signals"] = json.loads(d.pop("signals_json", "[]"))
        ej = d.pop("evidence_json", None)
        d["evidence"] = json.loads(ej) if ej else None
        # Get latest decision
        dec_row = conn.execute(
            "SELECT decision, note, timestamp FROM decisions "
            "WHERE review_id = ? ORDER BY id DESC LIMIT 1",
            (review_id,),
        ).fetchone()
        d["decision"] = dict(dec_row) if dec_row else None
        return d
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Decisions
# ---------------------------------------------------------------------------
def insert_decision(
    db_path: Path | str,
    review_id: int,
    decision: str,
    note: str = "",
) -> int:
    """Insert a reviewer decision linked to a review. Returns row id.

    Raises:
        ValueError: Bad decision value.
        KeyError: Unknown review_id (404).
    """
    if decision not in _VALID_DECISIONS:
        raise ValueError(
            f"Invalid decision '{decision}'. Must be one of: {sorted(_VALID_DECISIONS)}"
        )
    conn = _connect(Path(db_path))
    try:
        # Verify review exists
        exists = conn.execute(
            "SELECT id FROM reviews WHERE id = ?", (review_id,)
        ).fetchone()
        if exists is None:
            raise KeyError(f"Review {review_id} not found")

        timestamp = datetime.now(timezone.utc).isoformat()
        cursor = conn.execute(
            "INSERT INTO decisions (review_id, timestamp, decision, note) "
            "VALUES (?, ?, ?, ?)",
            (review_id, timestamp, decision, note),
        )
        conn.commit()
        return cursor.lastrowid  # type: ignore[return-value]
    finally:
        conn.close()


def list_decisions(db_path: Path | str) -> list[dict[str, Any]]:
    """Return all decisions (newest first), joined with review data."""
    conn = _connect(Path(db_path))
    try:
        rows = conn.execute(
            "SELECT d.id, d.timestamp, d.decision, d.note, d.review_id, "
            "       r.commit_ref, r.score, r.explanation_source "
            "FROM decisions d "
            "JOIN reviews r ON d.review_id = r.id "
            "ORDER BY d.id DESC"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_metrics(db_path: Path | str) -> dict[str, Any]:
    """Aggregate metrics for the dashboard."""
    conn = _connect(Path(db_path))
    try:
        total = conn.execute("SELECT COUNT(*) FROM reviews").fetchone()[0]
        avg_score = conn.execute("SELECT COALESCE(AVG(score), 0) FROM reviews").fetchone()[0]
        high = conn.execute("SELECT COUNT(*) FROM reviews WHERE score >= 70").fetchone()[0]
        medium = conn.execute(
            "SELECT COUNT(*) FROM reviews WHERE score >= 30 AND score < 70"
        ).fetchone()[0]
        low = conn.execute("SELECT COUNT(*) FROM reviews WHERE score < 30").fetchone()[0]
        fallback = conn.execute(
            "SELECT COUNT(*) FROM reviews WHERE explanation_source = 'local_fallback'"
        ).fetchone()[0]

        # Decision counts
        dec_counts: dict[str, int] = {}
        for row in conn.execute(
            "SELECT decision, COUNT(*) as cnt FROM decisions GROUP BY decision"
        ).fetchall():
            dec_counts[row["decision"]] = row["cnt"]

        pending = total - conn.execute(
            "SELECT COUNT(DISTINCT review_id) FROM decisions"
        ).fetchone()[0]

        return {
            "total_reviews": total,
            "avg_score": round(float(avg_score), 1),
            "risk_high": high,
            "risk_medium": medium,
            "risk_low": low,
            "decisions": {
                "pending": pending,
                "approve": dec_counts.get("approve", 0),
                "request_changes": dec_counts.get("request_changes", 0),
                "escalate": dec_counts.get("escalate", 0),
            },
            "fallback_explanation_rate": round(fallback / total, 3) if total else 0.0,
        }
    finally:
        conn.close()
