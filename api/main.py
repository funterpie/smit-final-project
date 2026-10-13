"""api/main.py — FastAPI backend serving the PR Risk Scorer dashboard.

Endpoints:
    POST /review          — score a commit (returns RiskReport JSON)
    GET  /decisions       — list audit log decisions
    POST /decisions       — log a human decision
    GET  /decisions/{id}  — get single decision
    GET  /health          — liveness check

Run:
    uvicorn api.main:app --reload --port 8000
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import AUDIT_DB_PATH, GROQ_API_KEY, INDEX_DIR, SIMILARITY_THRESHOLD
from features.schema import CommitFeatures
from models.risk_engine import compute_risk
from api.audit import insert_decision, list_decisions

app = FastAPI(
    title="PR Risk Scorer API",
    description="Just-in-time software defect prediction backend.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
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
    features: Optional[CommitFeatures] = None  # supply directly for offline demo
    include_rag: bool = True
    include_explain: bool = True


class DecisionRequest(BaseModel):
    commit_hash: str
    score: int
    decision: str  # approve | request_changes | escalate
    explanation: str = ""


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


def _try_rag(features: CommitFeatures) -> dict | None:
    try:
        from rag.retrieve import retrieve_evidence
        ev = retrieve_evidence(features, index_dir=str(INDEX_DIR), threshold=SIMILARITY_THRESHOLD)
        if ev is None:
            return None
        return {"commit_hash": ev.commit_hash, "similarity": ev.similarity, "summary": ev.summary}
    except Exception:
        return None


def _try_explain(report: object, evidence: dict | None) -> dict | None:
    try:
        from explain.llm_explain import explain_risk
        from rag.retrieve import RetrievedEvidence
        ev_obj = (
            RetrievedEvidence(**evidence)
            if evidence
            else None
        )
        expl = explain_risk(report, ev_obj, groq_api_key=GROQ_API_KEY)  # type: ignore
        return {"text": expl.text, "source": expl.source}
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/review")
def review(req: ReviewRequest) -> dict:
    """Score a commit. Supply either `features` directly or `repo_path` + `commit_hash`."""
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
    from rag.retrieve import RetrievedEvidence
    ev_obj = RetrievedEvidence(**evidence) if evidence else None
    explanation = _try_explain(report, evidence) if req.include_explain else None

    return {
        "commit_hash": req.commit_hash,
        **report.as_dict(),
        "evidence": evidence,
        "explanation": explanation,
    }


@app.get("/decisions")
def get_decisions(limit: int = 50) -> list[dict]:
    """Return audit log decisions (newest first)."""
    return list_decisions(AUDIT_DB_PATH)[:limit]


@app.post("/decisions")
def post_decision(req: DecisionRequest) -> dict:
    """Log a human reviewer decision."""
    try:
        row_id = insert_decision(
            AUDIT_DB_PATH,
            req.commit_hash,
            req.score,
            req.decision,
            req.explanation,
        )
        return {"id": row_id, "status": "logged"}
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
