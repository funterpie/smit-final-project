"""Configuration validation for the high-risk session change."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SecurityPolicy:
    signing_secret: bytes
    session_lifetime_seconds: int
    clock_skew_seconds: int
    maximum_active_sessions: int
    require_secure_transport: bool
    allowed_issuers: tuple[str, ...]

    @classmethod
    def from_mapping(cls, values: dict[str, object]) -> "SecurityPolicy":
        secret = values.get("signing_secret")
        lifetime = values.get("session_lifetime_seconds", 1800)
        skew = values.get("clock_skew_seconds", 60)
        maximum = values.get("maximum_active_sessions", 12)
        secure = values.get("require_secure_transport", True)
        issuers = values.get("allowed_issuers", ())
        if not isinstance(secret, bytes) or len(secret) < 32:
            raise ValueError("signing_secret must be at least 32 bytes")
        if not isinstance(lifetime, int) or not 60 <= lifetime <= 86400:
            raise ValueError("session lifetime must be between 60 and 86400 seconds")
        if not isinstance(skew, int) or not 0 <= skew <= 300:
            raise ValueError("clock skew must be between 0 and 300 seconds")
        if not isinstance(maximum, int) or not 1 <= maximum <= 100:
            raise ValueError("maximum active sessions must be between 1 and 100")
        if not isinstance(secure, bool):
            raise ValueError("require_secure_transport must be boolean")
        if not isinstance(issuers, (list, tuple)):
            raise ValueError("allowed_issuers must be a list or tuple")
        normalized_issuers = tuple(
            issuer.strip() for issuer in issuers
            if isinstance(issuer, str) and issuer.strip()
        )
        if not normalized_issuers:
            raise ValueError("at least one allowed issuer must be configured")
        return cls(
            signing_secret=secret,
            session_lifetime_seconds=lifetime,
            clock_skew_seconds=skew,
            maximum_active_sessions=maximum,
            require_secure_transport=secure,
            allowed_issuers=normalized_issuers,
        )

    def validate_issuer(self, issuer: str) -> bool:
        candidate = issuer.strip()
        return bool(candidate) and candidate in self.allowed_issuers

    def validate_transport(self, scheme: str) -> bool:
        normalized = scheme.lower()
        if self.require_secure_transport:
            return normalized == "https"
        return normalized in {"http", "https"}

    def session_is_current(self, issued_at: int, now: int) -> bool:
        if issued_at > now + self.clock_skew_seconds:
            return False
        if now - issued_at > self.session_lifetime_seconds:
            return False
        return True

    def can_create_session(self, active_count: int) -> bool:
        return 0 <= active_count < self.maximum_active_sessions
