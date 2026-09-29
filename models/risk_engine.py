"""models/risk_engine.py — Weighted signal combiner (real implementation).

Input:  CommitFeatures
Output: RiskReport  (score 0-100, breakdown of named signals)

Weights are intentionally simple and fixed for now; they will be calibrated
against AUC-PR once the baseline model is trained (see PLANNING.md Week 1).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from features.schema import CommitFeatures

# ---------------------------------------------------------------------------
# Named signal weights — adjust here to re-tune without touching logic
# ---------------------------------------------------------------------------
_LARGE_DIFF_LINES_THRESHOLD = 300  # total lines changed above which we flag
_HIGH_AUTHOR_BUG_RATE_THRESHOLD = 0.3  # 30 % of author's past commits linked to bugs

SIGNAL_WEIGHTS: dict[str, int] = {
    "large_diff": 25,
    "touches_sensitive_module": 30,
    "high_author_bug_rate": 20,
    "no_tests": 15,
    "high_dispersion": 10,
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

    def triggered_signals(self) -> list[SignalScore]:
        """Return only the signals that fired (triggered=True)."""
        return [s for s in self.signals if s.triggered]

    def as_text(self) -> str:
        """Human-readable single-line summary for CLI / audit output."""
        fired = ", ".join(s.name for s in self.triggered_signals()) or "none"
        return f"Risk score: {self.score}/100  |  Signals triggered: {fired}"


def compute_risk(features: CommitFeatures) -> RiskReport:
    """Compute a risk score from structured commit features.

    Args:
        features: A CommitFeatures instance produced by features.extract.

    Returns:
        A RiskReport containing the capped aggregate score and per-signal breakdown.
    """
    total_lines = features.lines_added + features.lines_removed

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
            triggered=features.dispersion > 3.0,
            description=(
                f"Change dispersion is {features.dispersion:.1f} "
                "(>3.0 indicates cross-cutting changes)."
            ),
        ),
    ]

    raw_score = sum(s.weight for s in signals if s.triggered)
    capped_score = min(raw_score, 100)

    return RiskReport(score=capped_score, signals=signals)
