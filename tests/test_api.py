"""tests/test_api.py — Endpoint tests for the FastAPI backend.

Covers:
    POST /review         — creates a review in SQLite
    GET  /reviews        — list + filter by risk / decision
    POST /decisions      — log decision (incl. 404 / invalid cases)
    GET  /audit          — audit trail
    GET  /metrics        — aggregate stats
    GET  /health         — liveness
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Use a temp DB so tests don't corrupt production data
_tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["AUDIT_DB_PATH"] = _tmp_db.name

# Must import AFTER patching env (config reads on import)
import importlib
import config as _cfg
_cfg.AUDIT_DB_PATH = Path(_tmp_db.name)

from api.main import app  # noqa: E402

client = TestClient(app)

# A minimal CommitFeatures payload for /review
_FEATURES_PAYLOAD = {
    "lines_added": 250,
    "lines_removed": 30,
    "files_touched": 5,
    "dispersion": 2.1,
    "author_bug_rate": 0.15,
    "hours_since_last_commit": 48.0,
    "tests_added": True,
    "touches_sensitive_module": False,
}


# ---------------------------------------------------------------------------
# /health
# ---------------------------------------------------------------------------
class TestHealth:
    def test_health_returns_ok(self) -> None:
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# POST /review
# ---------------------------------------------------------------------------
class TestReview:
    def test_review_with_inline_features(self) -> None:
        resp = client.post(
            "/review",
            json={
                "commit_hash": "abc123",
                "features": _FEATURES_PAYLOAD,
                "include_rag": False,
                "include_explain": False,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "review_id" in data
        assert "score" in data
        assert "signals" in data
        assert "explanation_source" in data
        assert isinstance(data["signals"], list)
        assert data["commit_hash"] == "abc123"

    def test_review_returns_explanation_source(self) -> None:
        resp = client.post(
            "/review",
            json={
                "commit_hash": "def456",
                "features": _FEATURES_PAYLOAD,
                "include_rag": False,
                "include_explain": True,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["explanation_source"] in ("groq", "local_fallback")
        assert "fallback_reason" in data


# ---------------------------------------------------------------------------
# GET /reviews
# ---------------------------------------------------------------------------
class TestGetReviews:
    def test_list_reviews_returns_list(self) -> None:
        resp = client.get("/reviews")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1  # from the POST /review tests above

    def test_filter_by_risk(self) -> None:
        # First create a low-risk review
        client.post(
            "/review",
            json={
                "commit_hash": "low_risk_1",
                "features": {
                    **_FEATURES_PAYLOAD,
                    "lines_added": 5,
                    "lines_removed": 2,
                    "files_touched": 1,
                    "dispersion": 0.1,
                    "author_bug_rate": 0.0,
                    "tests_added": True,
                    "touches_sensitive_module": False,
                },
                "include_rag": False,
                "include_explain": False,
            },
        )
        resp = client.get("/reviews?risk=low")
        assert resp.status_code == 200
        for r in resp.json():
            assert r["score"] < 30

    def test_filter_by_invalid_risk_returns_422(self) -> None:
        resp = client.get("/reviews?risk=INVALID")
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# POST /decisions
# ---------------------------------------------------------------------------
class TestDecisions:
    def test_post_decision_approve(self) -> None:
        # First create a review to reference
        review_resp = client.post(
            "/review",
            json={
                "commit_hash": "decision_test1",
                "features": _FEATURES_PAYLOAD,
                "include_rag": False,
                "include_explain": False,
            },
        )
        review_id = review_resp.json()["review_id"]

        resp = client.post(
            "/decisions",
            json={"review_id": review_id, "decision": "approve", "note": "Looks good"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "logged"
        assert "id" in data

    def test_post_decision_escalate(self) -> None:
        review_resp = client.post(
            "/review",
            json={
                "commit_hash": "decision_test2",
                "features": _FEATURES_PAYLOAD,
                "include_rag": False,
                "include_explain": False,
            },
        )
        review_id = review_resp.json()["review_id"]

        resp = client.post(
            "/decisions",
            json={"review_id": review_id, "decision": "escalate"},
        )
        assert resp.status_code == 200

    def test_post_decision_invalid_decision_returns_422(self) -> None:
        review_resp = client.post(
            "/review",
            json={
                "commit_hash": "decision_test3",
                "features": _FEATURES_PAYLOAD,
                "include_rag": False,
                "include_explain": False,
            },
        )
        review_id = review_resp.json()["review_id"]

        resp = client.post(
            "/decisions",
            json={"review_id": review_id, "decision": "yolo"},
        )
        assert resp.status_code == 422

    def test_post_decision_unknown_review_returns_404(self) -> None:
        resp = client.post(
            "/decisions",
            json={"review_id": 99999, "decision": "approve"},
        )
        assert resp.status_code == 404

    def test_filter_reviews_by_decision(self) -> None:
        resp = client.get("/reviews?decision=approve")
        assert resp.status_code == 200
        for r in resp.json():
            assert r["decision"] == "approve"

        resp_pending = client.get("/reviews?decision=pending")
        assert resp_pending.status_code == 200
        for r in resp_pending.json():
            assert r["decision"] is None


# ---------------------------------------------------------------------------
# GET /audit
# ---------------------------------------------------------------------------
class TestAudit:
    def test_audit_returns_list(self) -> None:
        resp = client.get("/audit")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        if data:
            row = data[0]
            assert "commit_ref" in row
            assert "score" in row
            assert "decision" in row
            assert "explanation_source" in row
            assert "timestamp" in row


# ---------------------------------------------------------------------------
# GET /metrics
# ---------------------------------------------------------------------------
class TestMetrics:
    def test_metrics_returns_expected_keys(self) -> None:
        resp = client.get("/metrics")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_reviews" in data
        assert "avg_score" in data
        assert "risk_high" in data
        assert "risk_medium" in data
        assert "risk_low" in data
        assert "decisions" in data
        assert "fallback_explanation_rate" in data
        assert data["total_reviews"] >= 1

    def test_metrics_decision_counts(self) -> None:
        resp = client.get("/metrics")
        data = resp.json()
        dec = data["decisions"]
        assert "pending" in dec
        assert "approve" in dec
        assert "request_changes" in dec
        assert "escalate" in dec


# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True, scope="session")
def cleanup() -> None:  # type: ignore[misc]
    yield  # type: ignore[misc]
    try:
        os.unlink(_tmp_db.name)
    except FileNotFoundError:
        pass
