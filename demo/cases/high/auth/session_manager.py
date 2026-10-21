"""Session token lifecycle for the high-risk synthetic demonstration case."""

from __future__ import annotations

import hashlib
import hmac
import secrets
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class SessionToken:
    token_id: str
    subject: str
    issued_at: int
    expires_at: int
    digest: str
    revoked: bool = False


class SessionManager:
    """Issue, validate, rotate, and revoke opaque session tokens."""

    def __init__(self, signing_secret: bytes, lifetime_seconds: int = 1800) -> None:
        if len(signing_secret) < 32:
            raise ValueError("session signing secret must contain at least 32 bytes")
        if lifetime_seconds < 60 or lifetime_seconds > 86400:
            raise ValueError("session lifetime is outside the supported range")
        self._secret = signing_secret
        self._lifetime = lifetime_seconds
        self._sessions: dict[str, SessionToken] = {}

    def issue(self, subject: str, now: int | None = None) -> tuple[str, SessionToken]:
        identity = subject.strip()
        if not identity:
            raise ValueError("session subject must not be empty")
        issued = int(time.time()) if now is None else now
        raw = secrets.token_urlsafe(32)
        token_id = secrets.token_hex(16)
        signature = self._sign(token_id, raw)
        token = f"{token_id}.{raw}.{signature}"
        record = SessionToken(
            token_id=token_id,
            subject=identity,
            issued_at=issued,
            expires_at=issued + self._lifetime,
            digest=self._digest(raw),
        )
        self._sessions[token_id] = record
        return token, record

    def validate(self, token: str, now: int | None = None) -> SessionToken | None:
        parsed = self._parse(token)
        if parsed is None:
            return None
        token_id, raw, signature = parsed
        expected_signature = self._sign(token_id, raw)
        if not hmac.compare_digest(signature, expected_signature):
            return None
        record = self._sessions.get(token_id)
        if record is None or record.revoked:
            return None
        if not hmac.compare_digest(record.digest, self._digest(raw)):
            return None
        current = int(time.time()) if now is None else now
        if current >= record.expires_at or current < record.issued_at:
            return None
        return record

    def rotate(self, token: str, now: int | None = None) -> tuple[str, SessionToken] | None:
        record = self.validate(token, now)
        if record is None:
            return None
        self.revoke(record.token_id)
        return self.issue(record.subject, now)

    def revoke(self, token_id: str) -> bool:
        record = self._sessions.get(token_id)
        if record is None or record.revoked:
            return False
        self._sessions[token_id] = SessionToken(
            token_id=record.token_id,
            subject=record.subject,
            issued_at=record.issued_at,
            expires_at=record.expires_at,
            digest=record.digest,
            revoked=True,
        )
        return True

    def revoke_subject(self, subject: str) -> int:
        identity = subject.strip()
        revoked = 0
        for token_id, record in list(self._sessions.items()):
            if record.subject == identity and self.revoke(token_id):
                revoked += 1
        return revoked

    def active_count(self, now: int | None = None) -> int:
        current = int(time.time()) if now is None else now
        return sum(
            1 for record in self._sessions.values()
            if not record.revoked and current < record.expires_at
        )

    def _parse(self, token: str) -> tuple[str, str, str] | None:
        parts = token.split(".")
        if len(parts) != 3 or any(not part for part in parts):
            return None
        token_id, raw, signature = parts
        if len(token_id) != 32 or len(signature) != 64:
            return None
        return token_id, raw, signature

    def _sign(self, token_id: str, raw: str) -> str:
        message = f"{token_id}.{raw}".encode("utf-8")
        return hmac.new(self._secret, message, hashlib.sha256).hexdigest()

    @staticmethod
    def _digest(raw: str) -> str:
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()
