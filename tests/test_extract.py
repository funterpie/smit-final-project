"""tests/test_extract.py — Tests for features/extract.py."""

import pytest
from features.extract import features_from_apachejit_row, _path_dispersion, _is_sensitive
from features.schema import CommitFeatures


class TestPathDispersion:
    def test_single_dir_is_zero_or_low(self) -> None:
        score = _path_dispersion(["src/foo.py", "src/bar.py", "src/baz.py"])
        # All in same top-level dir → low dispersion
        assert score < 2.0

    def test_many_dirs_is_high(self) -> None:
        score = _path_dispersion([
            "auth/login.py", "payment/checkout.py", "ui/form.py",
            "api/v1.py", "db/schema.py", "tests/test_all.py",
        ])
        assert score > 2.0

    def test_empty_returns_zero(self) -> None:
        assert _path_dispersion([]) == 0.0


class TestIsSensitive:
    def test_detects_auth_path(self) -> None:
        assert _is_sensitive("src/auth/login.py") is True

    def test_detects_crypto_path(self) -> None:
        assert _is_sensitive("lib/crypto/aes.py") is True

    def test_non_sensitive_path(self) -> None:
        assert _is_sensitive("src/utils/helpers.py") is False


class TestFeaturesFromApacheJITRow:
    def _sample_row(self, **overrides: str) -> dict[str, str]:
        base: dict[str, str] = {
            "commit_id": "abc123",
            "project": "apache/kafka",
            "buggy": "True",
            "la": "100",
            "ld": "20",
            "nf": "5",
            "ent": "2.3",
            "ndev": "1",
            "age": "1.5",   # months
            "nuc": "3",
            "aexp": "50",
            "arexp": "15",
            "asexp": "0.3",
        }
        base.update(overrides)
        return base

    def test_basic_mapping(self) -> None:
        row = self._sample_row()
        feat = features_from_apachejit_row(row)
        assert isinstance(feat, CommitFeatures)
        assert feat.lines_added == 100
        assert feat.lines_removed == 20
        assert feat.files_touched == 5
        assert feat.dispersion == 2.3

    def test_author_bug_rate_clamped(self) -> None:
        feat = features_from_apachejit_row(self._sample_row(aexp="0", arexp="999"))
        assert 0.0 <= feat.author_bug_rate <= 1.0

    def test_hours_from_age(self) -> None:
        feat = features_from_apachejit_row(self._sample_row(age="1.0"))
        # 1 month ≈ 720 hours
        assert feat.hours_since_last_commit > 0

    def test_missing_fields_default_to_zero(self) -> None:
        feat = features_from_apachejit_row({"la": "0", "ld": "0", "nf": "0"})
        assert feat.lines_added == 0
        assert feat.dispersion == 0.0
