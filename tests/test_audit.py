"""tests/test_audit.py — Pytest tests for api/audit.py.

Updated to match the two-table schema (reviews + decisions).
"""

import pytest
import sqlite3
from pathlib import Path

from api.audit import (
    insert_review,
    list_reviews,
    get_review,
    insert_decision,
    list_decisions,
    get_metrics,
)


@pytest.fixture()
def db(tmp_path: Path) -> Path:
    """Provide a fresh temporary SQLite database for each test."""
    return tmp_path / "test_audit.db"


def _insert_dummy_review(
    db: Path,
    commit_ref: str = "abc1234",
    score: int = 50,
) -> int:
    """Helper to insert a minimal review so we can attach decisions to it."""
    return insert_review(
        db_path=db,
        commit_ref=commit_ref,
        diff_hash="deadbeef",
        score=score,
        signals=[{"name": "test_signal", "value": 1, "weight": 10, "weighted": 10}],
        evidence=None,
        explanation="Test explanation",
        explanation_source="local_fallback",
    )


# -----------------------------------------------------------------------
# Reviews
# -----------------------------------------------------------------------
class TestInsertReview:
    def test_insert_returns_id(self, db: Path) -> None:
        rid = _insert_dummy_review(db, "abc1234", 45)
        assert isinstance(rid, int)
        assert rid >= 1

    def test_sequential_ids(self, db: Path) -> None:
        id1 = _insert_dummy_review(db, "abc0001", 10)
        id2 = _insert_dummy_review(db, "abc0002", 80)
        assert id2 > id1

    def test_review_retrievable(self, db: Path) -> None:
        rid = _insert_dummy_review(db, "abc1234", 60)
        review = get_review(db, rid)
        assert review is not None
        assert review["commit_ref"] == "abc1234"
        assert review["score"] == 60
        assert review["explanation"] == "Test explanation"

    def test_fallback_reason_round_trips(self, db: Path) -> None:
        rid = insert_review(
            db, "fallback-case", "", 20, [], None, "Local text", "local_fallback",
            fallback_reason="Groq request failed (BadRequestError)",
        )
        assert get_review(db, rid)["fallback_reason"] == "Groq request failed (BadRequestError)"

    def test_old_reviews_table_migrates_without_losing_rows(self, db: Path) -> None:
        with sqlite3.connect(db) as conn:
            conn.execute("""CREATE TABLE reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT NOT NULL,
                commit_ref TEXT NOT NULL, diff_hash TEXT NOT NULL DEFAULT '',
                score INTEGER NOT NULL, signals_json TEXT NOT NULL DEFAULT '[]',
                evidence_json TEXT, explanation TEXT NOT NULL DEFAULT '',
                explanation_source TEXT NOT NULL DEFAULT 'local_fallback'
            )""")
            conn.execute("INSERT INTO reviews(timestamp, commit_ref, score) VALUES ('old', 'old-row', 12)")
        row = get_review(db, 1)
        assert row is not None
        assert row["commit_ref"] == "old-row"
        assert row["fallback_reason"] is None

    def test_review_signals_parsed(self, db: Path) -> None:
        rid = _insert_dummy_review(db)
        review = get_review(db, rid)
        assert isinstance(review["signals"], list)
        assert review["signals"][0]["name"] == "test_signal"


class TestListReviews:
    def test_empty_db(self, db: Path) -> None:
        assert list_reviews(db) == []

    def test_sorted_by_score_desc(self, db: Path) -> None:
        _insert_dummy_review(db, "low", 10)
        _insert_dummy_review(db, "high", 90)
        _insert_dummy_review(db, "mid", 50)
        rows = list_reviews(db)
        scores = [r["score"] for r in rows]
        assert scores == sorted(scores, reverse=True)

    def test_risk_filter_high(self, db: Path) -> None:
        _insert_dummy_review(db, "low", 10)
        _insert_dummy_review(db, "high", 90)
        rows = list_reviews(db, risk="high")
        assert all(r["score"] >= 70 for r in rows)
        assert len(rows) == 1

    def test_risk_filter_low(self, db: Path) -> None:
        _insert_dummy_review(db, "low", 10)
        _insert_dummy_review(db, "high", 90)
        rows = list_reviews(db, risk="low")
        assert all(r["score"] < 30 for r in rows)
        assert len(rows) == 1


# -----------------------------------------------------------------------
# Decisions
# -----------------------------------------------------------------------
class TestInsertDecision:
    def test_insert_returns_id(self, db: Path) -> None:
        review_id = _insert_dummy_review(db, "abc1234", 45)
        row_id = insert_decision(db, review_id, "approve")
        assert isinstance(row_id, int)
        assert row_id >= 1

    def test_sequential_ids(self, db: Path) -> None:
        r1 = _insert_dummy_review(db, "abc0001", 10)
        r2 = _insert_dummy_review(db, "abc0002", 80)
        id1 = insert_decision(db, r1, "approve")
        id2 = insert_decision(db, r2, "escalate")
        assert id2 > id1

    def test_invalid_decision_raises(self, db: Path) -> None:
        review_id = _insert_dummy_review(db)
        with pytest.raises(ValueError, match="Invalid decision"):
            insert_decision(db, review_id, "rubber_stamp")

    def test_nonexistent_review_raises(self, db: Path) -> None:
        with pytest.raises(KeyError, match="not found"):
            insert_decision(db, 99999, "approve")

    def test_note_stored(self, db: Path) -> None:
        review_id = _insert_dummy_review(db, "abc1234", 60)
        insert_decision(db, review_id, "request_changes", note="Too risky")
        rows = list_decisions(db)
        assert rows[0]["note"] == "Too risky"


class TestListDecisions:
    def test_empty_db_returns_empty_list(self, db: Path) -> None:
        assert list_decisions(db) == []

    def test_most_recent_first(self, db: Path) -> None:
        r1 = _insert_dummy_review(db, "first_commit", 10)
        r2 = _insert_dummy_review(db, "second_commit", 90)
        insert_decision(db, r1, "approve")
        insert_decision(db, r2, "escalate")
        rows = list_decisions(db)
        assert rows[0]["commit_ref"] == "second_commit"
        assert rows[1]["commit_ref"] == "first_commit"

    def test_all_fields_present(self, db: Path) -> None:
        review_id = _insert_dummy_review(db, "deadbeef", 55)
        insert_decision(db, review_id, "request_changes", note="review note")
        row = list_decisions(db)[0]
        expected_keys = {
            "id", "timestamp", "decision", "note",
            "review_id", "commit_ref", "score", "explanation_source",
        }
        assert set(row.keys()) == expected_keys

    def test_all_valid_decisions(self, db: Path) -> None:
        for decision in ("approve", "request_changes", "escalate"):
            rid = _insert_dummy_review(db, f"commit_{decision}", 50)
            insert_decision(db, rid, decision)
        assert len(list_decisions(db)) == 3


# -----------------------------------------------------------------------
# Metrics
# -----------------------------------------------------------------------
class TestMetrics:
    def test_empty_db(self, db: Path) -> None:
        m = get_metrics(db)
        assert m["total_reviews"] == 0
        assert m["avg_score"] == 0
        assert m["decisions"]["pending"] == 0

    def test_counts_match(self, db: Path) -> None:
        _insert_dummy_review(db, "a", 10)
        _insert_dummy_review(db, "b", 50)
        _insert_dummy_review(db, "c", 90)
        m = get_metrics(db)
        assert m["total_reviews"] == 3
        assert m["risk_high"] == 1
        assert m["risk_medium"] == 1
        assert m["risk_low"] == 1

    def test_pending_count(self, db: Path) -> None:
        r1 = _insert_dummy_review(db, "a", 50)
        _insert_dummy_review(db, "b", 50)
        insert_decision(db, r1, "approve")
        m = get_metrics(db)
        assert m["decisions"]["pending"] == 1
        assert m["decisions"]["approve"] == 1
