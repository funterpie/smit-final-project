"""features/schema.py — Typed data model for commit features.

This is the central schema that flows through the entire pipeline:
  extract_features → risk_engine → (baseline / codebert) → rag → llm_explain

All model-facing functions receive a CommitFeatures instance, never raw diff text.
"""

from pydantic import BaseModel, Field


class CommitFeatures(BaseModel):
    """Structured representation of a single commit's risk-relevant features.

    Populated by features.extract.extract_features() and consumed by the
    risk engine, baseline model, CodeBERT model, and RAG retriever.
    """

    lines_added: int = Field(..., ge=0, description="Total lines added in the commit.")
    lines_removed: int = Field(..., ge=0, description="Total lines removed in the commit.")
    files_touched: int = Field(..., ge=0, description="Number of distinct files modified.")
    dispersion: float = Field(
        ...,
        ge=0.0,
        description=(
            "Measure of how spread-out the changes are across the directory tree. "
            "Higher values (e.g. >3) suggest cross-cutting, higher-risk changes."
        ),
    )
    author_bug_rate: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description=(
            "Historical fraction of this author's commits that were later linked to bugs "
            "(repo-specific, not global). Range [0.0, 1.0]."
        ),
    )
    hours_since_last_commit: float = Field(
        ...,
        ge=0.0,
        description=(
            "Hours elapsed since the same author's previous commit to this repo. "
            "Very short gaps may indicate rushed work."
        ),
    )
    tests_added: bool = Field(
        ...,
        description="True if the commit contains at least one test file addition or modification.",
    )
    touches_sensitive_module: bool = Field(
        ...,
        description=(
            "True if any changed file is inside a module flagged as security/critical "
            "(e.g. auth/, crypto/, payment/)."
        ),
    )
