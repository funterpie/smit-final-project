"""Small, defensive parser used by the low-risk demonstration case."""

from __future__ import annotations


def parse_revision(value: str) -> str:
    """Return a normalized revision token or reject empty input."""
    revision = value.strip()
    if not revision:
        raise ValueError("revision must not be empty")
    return revision.lower()
