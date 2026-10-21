"""Persistence adapter for security-sensitive session state."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

from auth.session_manager import SessionToken


class SessionStore:
    """Store token metadata and revocation state without raw tokens."""

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._path, timeout=5.0)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 5000")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute("PRAGMA journal_mode = WAL")
            connection.execute(
                """CREATE TABLE IF NOT EXISTS sessions (
                    token_id TEXT PRIMARY KEY,
                    subject TEXT NOT NULL,
                    issued_at INTEGER NOT NULL,
                    expires_at INTEGER NOT NULL,
                    digest TEXT NOT NULL,
                    revoked INTEGER NOT NULL DEFAULT 0,
                    updated_at INTEGER NOT NULL
                )"""
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS sessions_subject_idx ON sessions(subject)"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS sessions_expiry_idx ON sessions(expires_at)"
            )

    def save(self, record: SessionToken, now: int) -> None:
        with self._connect() as connection:
            connection.execute(
                """INSERT INTO sessions
                   (token_id, subject, issued_at, expires_at, digest, revoked, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(token_id) DO UPDATE SET
                     subject=excluded.subject,
                     issued_at=excluded.issued_at,
                     expires_at=excluded.expires_at,
                     digest=excluded.digest,
                     revoked=excluded.revoked,
                     updated_at=excluded.updated_at""",
                (
                    record.token_id,
                    record.subject,
                    record.issued_at,
                    record.expires_at,
                    record.digest,
                    int(record.revoked),
                    now,
                ),
            )

    def find(self, token_id: str) -> SessionToken | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT token_id, subject, issued_at, expires_at, digest, revoked "
                "FROM sessions WHERE token_id = ?",
                (token_id,),
            ).fetchone()
        if row is None:
            return None
        return SessionToken(
            token_id=row["token_id"],
            subject=row["subject"],
            issued_at=row["issued_at"],
            expires_at=row["expires_at"],
            digest=row["digest"],
            revoked=bool(row["revoked"]),
        )

    def revoke(self, token_id: str, now: int) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                "UPDATE sessions SET revoked = 1, updated_at = ? "
                "WHERE token_id = ? AND revoked = 0",
                (now, token_id),
            )
        return cursor.rowcount == 1

    def revoke_subject(self, subject: str, now: int) -> int:
        with self._connect() as connection:
            cursor = connection.execute(
                "UPDATE sessions SET revoked = 1, updated_at = ? "
                "WHERE subject = ? AND revoked = 0",
                (now, subject),
            )
        return cursor.rowcount

    def delete_expired(self, now: int, retain_revoked: bool = True) -> int:
        predicate = "expires_at < ? AND revoked = 0" if retain_revoked else "expires_at < ?"
        with self._connect() as connection:
            cursor = connection.execute(
                f"DELETE FROM sessions WHERE {predicate}", (now,)
            )
        return cursor.rowcount

    def list_for_subject(self, subject: str) -> Iterable[SessionToken]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT token_id, subject, issued_at, expires_at, digest, revoked "
                "FROM sessions WHERE subject = ? ORDER BY issued_at DESC",
                (subject,),
            ).fetchall()
        return [
            SessionToken(
                token_id=row["token_id"],
                subject=row["subject"],
                issued_at=row["issued_at"],
                expires_at=row["expires_at"],
                digest=row["digest"],
                revoked=bool(row["revoked"]),
            )
            for row in rows
        ]
