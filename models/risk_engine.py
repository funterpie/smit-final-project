"""models/risk_engine.py — Weighted signal combiner with optional ML probability blend.

Input:  CommitFeatures (+ optional baseline/CodeBERT probability)
Output: RiskReport  (score 0-100, breakdown of named signals)

Signal weights (fixed, calibrated heuristically):
    large_diff            25
    touches_sensitive     30
    high_author_bug_rate  20
    no_tests              15
    high_dispersion       10

When a baseline or CodeBERT probability is supplied, it scales a 20-point
bonus signal on top of the heuristic signals, giving a maximum of 120 raw
points which is still capped at 100. This lets the ML model boost borderline
commits without overriding the interpretable signal breakdown.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from features.schema import CommitFeatures

# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------
_LARGE_DIFF_LINES_THRESHOLD = 300
_HIGH_AUTHOR_BUG_RATE_THRESHOLD = 0.3
_HIGH_DISPERSION_THRESHOLD = 3.0
_ML_PROB_THRESHOLD = 0.5   # above this, ML signal fires

SIGNAL_WEIGHTS: dict[str, int] = {
    "large_diff": 25,
    "touches_sensitive_module": 30,
    "high_author_bug_rate": 20,
    "no_tests": 15,
    "high_dispersion": 10,
    "ml_model_flag": 20,   # ML probability-based bonus signal
}


@dataclass
class SignalScore:
    """A single named signal that contributed to the overall risk score."""

    name: str
    weight: int
    triggered: bool
    description: str


@dataclass
class RiskReport:
    """Output of the weighted risk engine for a single commit."""

    score: int  # 0-100, capped
    signals: list[SignalScore] = field(default_factory=list)
    baseline_prob: float | None = None   # raw ML probability if available
    codebert_prob: float | None = None   # CodeBERT probability if available

    def triggered_signals(self) -> list[SignalScore]:
        """Return only the signals that fired (triggered=True)."""
        return [s for s in self.signals if s.triggered]

    def as_text(self) -> str:
        """Human-readable single-line summary for CLI / audit output."""
        fired = ", ".join(s.name for s in self.triggered_signals()) or "none"
        ml_info = ""
        if self.baseline_prob is not None:
            ml_info = f"  |  Baseline prob: {self.baseline_prob:.2f}"
        if self.codebert_prob is not None:
            ml_info += f"  |  CodeBERT prob: {self.codebert_prob:.2f}"
        return f"Risk score: {self.score}/100  |  Signals triggered: {fired}{ml_info}"

    def as_dict(self) -> dict:
        """Serialisable dict for API / CLI JSON output."""
        return {
            "score": self.score,
            "baseline_prob": self.baseline_prob,
            "codebert_prob": self.codebert_prob,
            "signals": [
                {
                    "name": s.name,
                    "weight": s.weight,
                    "triggered": s.triggered,
                    "description": s.description,
                }
                for s in self.signals
            ],
        }


def compute_risk(
    features: CommitFeatures,
    baseline_prob: float | None = None,
    codebert_prob: float | None = None,
) -> RiskReport:
    """Compute a risk score from structured commit features.

    Args:
        features: A CommitFeatures instance produced by features.extract.
        baseline_prob: Optional bug probability from the sklearn baseline model.
            If supplied, adds a blended ML signal (up to +20 points).
        codebert_prob: Optional bug probability from fine-tuned CodeBERT.
            If both are supplied, the higher of the two is used for the ML signal.

    Returns:
        A RiskReport containing the capped aggregate score and per-signal breakdown.
    """
    total_lines = features.lines_added + features.lines_removed

    # Use the higher of the two ML probabilities when blending
    ml_prob: float | None = None
    if baseline_prob is not None and codebert_prob is not None:
        ml_prob = max(baseline_prob, codebert_prob)
    elif baseline_prob is not None:
        ml_prob = baseline_prob
    elif codebert_prob is not None:
        ml_prob = codebert_prob

    ml_triggered = ml_prob is not None and ml_prob > _ML_PROB_THRESHOLD

    signals: list[SignalScore] = [
        SignalScore(
            name="large_diff",
            weight=SIGNAL_WEIGHTS["large_diff"],
            triggered=total_lines > _LARGE_DIFF_LINES_THRESHOLD,
            description=(
                f"Diff has {total_lines} lines changed "
                f"(threshold: >{_LARGE_DIFF_LINES_THRESHOLD})."
            ),
        ),
        SignalScore(
            name="touches_sensitive_module",
            weight=SIGNAL_WEIGHTS["touches_sensitive_module"],
            triggered=features.touches_sensitive_module,
            description="At least one changed file is inside a security-critical module.",
        ),
        SignalScore(
            name="high_author_bug_rate",
            weight=SIGNAL_WEIGHTS["high_author_bug_rate"],
            triggered=features.author_bug_rate > _HIGH_AUTHOR_BUG_RATE_THRESHOLD,
            description=(
                f"Author's historical bug rate is {features.author_bug_rate:.0%} "
                f"(threshold: >{_HIGH_AUTHOR_BUG_RATE_THRESHOLD:.0%})."
            ),
        ),
        SignalScore(
            name="no_tests",
            weight=SIGNAL_WEIGHTS["no_tests"],
            triggered=not features.tests_added,
            description="No test files were added or modified in this commit.",
        ),
        SignalScore(
            name="high_dispersion",
            weight=SIGNAL_WEIGHTS["high_dispersion"],
            triggered=features.dispersion > _HIGH_DISPERSION_THRESHOLD,
            description=(
                f"Change dispersion is {features.dispersion:.1f} "
                f"(>{_HIGH_DISPERSION_THRESHOLD} indicates cross-cutting changes)."
            ),
        ),
        SignalScore(
            name="ml_model_flag",
            weight=SIGNAL_WEIGHTS["ml_model_flag"],
            triggered=ml_triggered,
            description=(
                f"ML model probability {ml_prob:.2f} exceeds threshold {_ML_PROB_THRESHOLD}."
                if ml_prob is not None
                else "No ML model probability available."
            ),
        ),
    ]

    raw_score = sum(s.weight for s in signals if s.triggered)
    capped_score = min(raw_score, 100)

    return RiskReport(
        score=capped_score,
        signals=signals,
        baseline_prob=baseline_prob,
        codebert_prob=codebert_prob,
    )
