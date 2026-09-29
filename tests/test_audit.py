"""tests/test_audit.py — Pytest tests for api/audit.py."""

import pytest
from pathlib import Path

from api.audit import insert_decision, list_decisions


@pytest.fixture()
def db(tmp_path: Path) -> Path:
    """Provide a fresh temporary SQLite database for each test."""
    return tmp_path / "test_audit.db"


class TestInsertDecision:
    def test_insert_returns_id(self, db: Path) -> None:
        row_id = insert_decision(db, "abc1234", 45, "approve")
        assert isinstance(row_id, int)
        assert row_id >= 1

    def test_sequential_ids(self, db: Path) -> None:
        id1 = insert_decision(db, "abc0001", 10, "approve")
        id2 = insert_decision(db, "abc0002", 80, "escalate")
        assert id2 > id1

    def test_invalid_decision_raises(self, db: Path) -> None:
        with pytest.raises(ValueError, match="Invalid decision"):
            insert_decision(db, "abc1234", 50, "rubber_stamp")

    def test_explanation_stored(self, db: Path) -> None:
        insert_decision(db, "abc1234", 60, "request_changes", explanation="Too risky")
        rows = list_decisions(db)
        assert rows[0]["explanation"] == "Too risky"


class TestListDecisions:
    def test_empty_db_returns_empty_list(self, db: Path) -> None:
        assert list_decisions(db) == []

    def test_most_recent_first(self, db: Path) -> None:
        insert_decision(db, "first_commit", 10, "approve")
        insert_decision(db, "second_commit", 90, "escalate")
        rows = list_decisions(db)
        assert rows[0]["commit_hash"] == "second_commit"
        assert rows[1]["commit_hash"] == "first_commit"

    def test_all_fields_present(self, db: Path) -> None:
        insert_decision(db, "deadbeef", 55, "request_changes", "Some explanation")
        row = list_decisions(db)[0]
        assert set(row.keys()) == {"id", "timestamp", "commit_hash", "score", "explanation", "decision"}

    def test_all_valid_decisions(self, db: Path) -> None:
        for decision in ("approve", "request_changes", "escalate"):
            insert_decision(db, "abc1234", 50, decision)
        assert len(list_decisions(db)) == 3
