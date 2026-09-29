"""tests/test_risk_engine.py — Pytest tests for models/risk_engine.py."""

import pytest

from features.schema import CommitFeatures
from models.risk_engine import RiskReport, SignalScore, compute_risk


def _features(**overrides: object) -> CommitFeatures:
    """Return a safe baseline CommitFeatures, allowing selective overrides."""
    defaults: dict[str, object] = {
        "lines_added": 10,
        "lines_removed": 5,
        "files_touched": 2,
        "dispersion": 1.0,
        "author_bug_rate": 0.1,
        "hours_since_last_commit": 24.0,
        "tests_added": True,
        "touches_sensitive_module": False,
    }
    defaults.update(overrides)
    return CommitFeatures(**defaults)  # type: ignore[arg-type]


class TestLowRiskCommit:
    """A clean, small commit should score 0."""

    def test_score_is_zero(self) -> None:
        report = compute_risk(_features())
        assert report.score == 0

    def test_no_signals_triggered(self) -> None:
        report = compute_risk(_features())
        assert report.triggered_signals() == []


class TestSingleSignals:
    """Each signal should add exactly its stated weight when triggered in isolation."""

    def test_large_diff_adds_25(self) -> None:
        report = compute_risk(_features(lines_added=250, lines_removed=100))  # 350 total
        assert report.score == 25

    def test_sensitive_module_adds_30(self) -> None:
        report = compute_risk(_features(touches_sensitive_module=True))
        assert report.score == 30

    def test_high_author_bug_rate_adds_20(self) -> None:
        report = compute_risk(_features(author_bug_rate=0.5))
        assert report.score == 20

    def test_no_tests_adds_15(self) -> None:
        report = compute_risk(_features(tests_added=False))
        assert report.score == 15

    def test_high_dispersion_adds_10(self) -> None:
        report = compute_risk(_features(dispersion=4.0))
        assert report.score == 10


class TestScoreCap:
    """Score must never exceed 100, even when all signals fire."""

    def test_all_signals_capped_at_100(self) -> None:
        report = compute_risk(
            _features(
                lines_added=200,
                lines_removed=200,
                touches_sensitive_module=True,
                author_bug_rate=0.9,
                tests_added=False,
                dispersion=5.0,
            )
        )
        assert report.score <= 100

    def test_all_signals_triggered(self) -> None:
        report = compute_risk(
            _features(
                lines_added=200,
                lines_removed=200,
                touches_sensitive_module=True,
                author_bug_rate=0.9,
                tests_added=False,
                dispersion=5.0,
            )
        )
        # All 5 signals triggered → 25+30+20+15+10 = 100
        assert len(report.triggered_signals()) == 5
        assert report.score == 100


class TestRiskReportHelpers:
    """Unit tests for RiskReport helper methods."""

    def test_as_text_contains_score(self) -> None:
        report = compute_risk(_features(tests_added=False))
        text = report.as_text()
        assert "15" in text
        assert "no_tests" in text

    def test_as_text_no_signals(self) -> None:
        report = compute_risk(_features())
        assert "none" in report.as_text()
