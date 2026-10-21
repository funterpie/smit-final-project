"""tests/test_explain.py — Tests for explain/llm_explain.py."""

import pytest
from types import SimpleNamespace
from unittest.mock import Mock

from features.schema import CommitFeatures
from models.risk_engine import compute_risk, RiskReport
from explain.llm_explain import explain_risk, Explanation, _local_fallback
from rag.retrieve import RetrievedEvidence


def _make_report(tests_added: bool = False, author_bug_rate: float = 0.5) -> RiskReport:
    feat = CommitFeatures(
        lines_added=400,
        lines_removed=5,
        files_touched=3,
        dispersion=1.0,
        author_bug_rate=author_bug_rate,
        hours_since_last_commit=2.0,
        tests_added=tests_added,
        touches_sensitive_module=False,
    )
    return compute_risk(feat)


class TestLocalFallback:
    def test_low_risk_fallback(self) -> None:
        feat = CommitFeatures(
            lines_added=5, lines_removed=2, files_touched=1,
            dispersion=0.5, author_bug_rate=0.0, hours_since_last_commit=8.0,
            tests_added=True, touches_sensitive_module=False,
        )
        report = compute_risk(feat)
        text = _local_fallback(report, evidence=None)
        assert "low risk" in text.lower() or "0" in text

    def test_high_risk_fallback_mentions_signals(self) -> None:
        report = _make_report(tests_added=False)
        text = _local_fallback(report, evidence=None)
        # Should mention at least one triggered signal
        assert any(s.name in text for s in report.triggered_signals())

    def test_fallback_with_evidence(self) -> None:
        report = _make_report()
        evidence = RetrievedEvidence(
            commit_hash="deadbeef", similarity=0.85, summary="KAFKA auth bug"
        )
        text = _local_fallback(report, evidence=evidence)
        assert "deadbeef" in text or "similarity" in text.lower()

    def test_fallback_without_evidence_says_no_match(self) -> None:
        report = _make_report()
        text = _local_fallback(report, evidence=None)
        assert "no" in text.lower()


class TestExplainRisk:
    def test_empty_key_uses_local_fallback(self) -> None:
        report = _make_report()
        result = explain_risk(report, evidence=None, groq_api_key="")
        assert isinstance(result, Explanation)
        assert result.source == "local_fallback"
        assert len(result.text) > 10

    def test_groq_exception_uses_fallback_and_does_not_log_key(self, monkeypatch, caplog) -> None:
        """Groq diagnostics are logged with secrets removed from the full error text."""
        import groq

        report = _make_report()
        secret = "test-secret-groq-key"
        create = Mock(side_effect=RuntimeError(f"BadRequestError: retired model, key={secret}"))
        client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
        monkeypatch.setattr(groq, "Groq", lambda api_key: client)
        result = explain_risk(report, evidence=None, groq_api_key=secret)
        assert isinstance(result, Explanation)
        assert result.source == "local_fallback"
        assert result.fallback_reason == "Groq request failed (RuntimeError)"
        assert "BadRequestError: retired model" in caplog.text
        assert secret not in caplog.text
        assert "[Groq API unavailable" not in result.text

    def test_local_fallback_text_has_no_error_prefix(self) -> None:
        result = explain_risk(_make_report(), groq_api_key="")
        assert "[Groq API unavailable" not in result.text
        assert result.source == "local_fallback"
        assert result.fallback_reason
