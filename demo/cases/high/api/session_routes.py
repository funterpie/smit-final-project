"""HTTP handlers for issuing and revoking security-sensitive sessions."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from auth.session_manager import SessionManager
from database.session_store import SessionStore


@dataclass(frozen=True)
class SessionResponse:
    status: int
    body: dict[str, Any]


class SessionRoutes:
    """Validate request fields before connecting session management layers."""

    def __init__(self, manager: SessionManager, store: SessionStore) -> None:
        self._manager = manager
        self._store = store

    def create(self, payload: dict[str, Any], now: int | None = None) -> SessionResponse:
        subject = self._string(payload.get("subject"))
        if subject is None:
            return SessionResponse(400, {"error": "subject is required"})
        current = int(time.time()) if now is None else now
        try:
            raw_token, record = self._manager.issue(subject, current)
        except ValueError:
            return SessionResponse(400, {"error": "session could not be created"})
        self._store.save(record, current)
        return SessionResponse(
            201,
            {
                "access_token": raw_token,
                "token_type": "Bearer",
                "expires_at": record.expires_at,
            },
        )

    def inspect(self, authorization: str | None, now: int | None = None) -> SessionResponse:
        token = self._bearer(authorization)
        if token is None:
            return SessionResponse(401, {"error": "valid bearer token required"})
        current = int(time.time()) if now is None else now
        record = self._manager.validate(token, current)
        if record is None:
            return SessionResponse(401, {"error": "session is invalid or expired"})
        persisted = self._store.find(record.token_id)
        if persisted is None or persisted.revoked:
            return SessionResponse(401, {"error": "session has been revoked"})
        return SessionResponse(
            200,
            {"subject": record.subject, "expires_at": record.expires_at},
        )

    def revoke(self, authorization: str | None, now: int | None = None) -> SessionResponse:
        token = self._bearer(authorization)
        if token is None:
            return SessionResponse(401, {"error": "valid bearer token required"})
        record = self._manager.validate(token, now)
        if record is None:
            return SessionResponse(401, {"error": "session is invalid or expired"})
        changed = self._store.revoke(record.token_id, int(time.time()) if now is None else now)
        self._manager.revoke(record.token_id)
        return SessionResponse(200, {"revoked": changed})

    @staticmethod
    def _bearer(header: str | None) -> str | None:
        if not header:
            return None
        scheme, separator, value = header.partition(" ")
        if not separator or scheme.lower() != "bearer" or not value.strip():
            return None
        return value.strip()

    @staticmethod
    def _string(value: Any) -> str | None:
        if not isinstance(value, str):
            return None
        normalized = value.strip()
        if not normalized or len(normalized) > 200:
            return None
        return normalized
