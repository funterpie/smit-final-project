"""api/main.py — FastAPI backend serving the PR Risk Scorer dashboard.

Endpoints:
    POST /review              — score a commit, persist to SQLite
    GET  /reviews             — list reviews (?risk=high|medium|low&decision=pending|…)
    POST /decisions           — log a human decision for a review
    GET  /audit               — audit trail (timestamp, commit, score, source, decision)
    GET  /metrics             — aggregate stats
    GET  /health              — liveness check

Run:
    uvicorn api.main:app --reload --port 8000
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import AUDIT_DB_PATH, GROQ_API_KEY, INDEX_DIR, SIMILARITY_THRESHOLD
from features.schema import CommitFeatures
from models.risk_engine import compute_risk
from api.audit import (
    insert_review,
    list_reviews,
    get_review,
    insert_decision,
    list_decisions,
    get_metrics,
)

app = FastAPI(
    title="PR Risk Scorer API",
    description="Just-in-time software defect prediction backend.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class ReviewRequest(BaseModel):
    commit_hash: str
    repo_path: str = "."
    diff_text: str = ""  # raw diff text (hashed, NOT stored or sent to LLM)
    features: Optional[CommitFeatures] = None
    include_rag: bool = True
    include_explain: bool = True


class DecisionRequest(BaseModel):
    review_id: int
    decision: str  # approve | request_changes | escalate
    note: str = ""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _try_baseline_prob(features: CommitFeatures) -> float | None:
    try:
        from models.baseline import predict_baseline
        return predict_baseline(features, model="rf")
    except FileNotFoundError:
        return None


def _try_codebert_prob(features: CommitFeatures) -> float | None:
    try:
        from models.codebert import predict_codebert
        return predict_codebert(features)
    except FileNotFoundError:
        return None


def _try_rag(features: CommitFeatures) -> dict[str, Any] | None:
    try:
        from rag.retrieve import retrieve_evidence
        ev = retrieve_evidence(features, index_dir=str(INDEX_DIR), threshold=SIMILARITY_THRESHOLD)
        if ev is None:
            return None
        return {"commit_hash": ev.commit_hash, "similarity": ev.similarity, "summary": ev.summary}
    except Exception:
        return None


def _try_explain(
    report: object, evidence: dict[str, Any] | None
) -> dict[str, str] | None:
    try:
        from explain.llm_explain import explain_risk
        from rag.retrieve import RetrievedEvidence
        ev_obj = RetrievedEvidence(**evidence) if evidence else None
        expl = explain_risk(report, ev_obj, groq_api_key=GROQ_API_KEY)  # type: ignore
        return {"text": expl.text, "source": expl.source}
    except Exception:
        return None


def _diff_hash(diff_text: str) -> str:
    """SHA-256 of the raw diff text. The diff itself is NEVER stored."""
    return hashlib.sha256(diff_text.encode()).hexdigest() if diff_text else ""


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/review")
def review(req: ReviewRequest) -> dict[str, Any]:
    """Score a commit. Persists to SQLite and returns full result."""
    if req.features:
        features = req.features
    else:
        try:
            from features.extract import extract_features
            features = extract_features(req.repo_path, req.commit_hash)
        except Exception as exc:
            raise HTTPException(status_code=422, detail=f"Feature extraction failed: {exc}")

    baseline_prob = _try_baseline_prob(features)
    codebert_prob = _try_codebert_prob(features)
    report = compute_risk(features, baseline_prob=baseline_prob, codebert_prob=codebert_prob)

    evidence = _try_rag(features) if req.include_rag else None
    explanation = _try_explain(report, evidence) if req.include_explain else None

    diff_h = _diff_hash(req.diff_text)
    explanation_text = explanation["text"] if explanation else ""
    explanation_source = explanation["source"] if explanation else "local_fallback"

    # Persist to SQLite
    review_id = insert_review(
        db_path=AUDIT_DB_PATH,
        commit_ref=req.commit_hash,
        diff_hash=diff_h,
        score=report.score,
        signals=report.as_dict()["signals"],
        evidence=evidence,
        explanation=explanation_text,
        explanation_source=explanation_source,
    )

    return {
        "review_id": review_id,
        "commit_hash": req.commit_hash,
        **report.as_dict(),
        "evidence": evidence,
        "explanation": explanation_text,
        "explanation_source": explanation_source,
    }


@app.get("/reviews")
def get_reviews(
    risk: Optional[str] = Query(None, pattern="^(high|medium|low)$"),
    decision: Optional[str] = Query(
        None, pattern="^(pending|approve|request_changes|escalate)$"
    ),
) -> list[dict[str, Any]]:
    """List reviews sorted by score DESC, with optional filters."""
    return list_reviews(AUDIT_DB_PATH, risk=risk, decision=decision)


@app.post("/decisions")
def post_decision(req: DecisionRequest) -> dict[str, Any]:
    """Log a human decision for a review."""
    try:
        row_id = insert_decision(
            AUDIT_DB_PATH,
            req.review_id,
            req.decision,
            req.note,
        )
        return {"id": row_id, "status": "logged"}
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.get("/audit")
def audit() -> list[dict[str, Any]]:
    """Audit trail: timestamp, commit, score, explanation_source, decision."""
    return list_decisions(AUDIT_DB_PATH)


@app.get("/metrics")
def metrics() -> dict[str, Any]:
    """Aggregate dashboard metrics."""
    return get_metrics(AUDIT_DB_PATH)
