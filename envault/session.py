"""Session management: cache the vault password in-memory for a TTL period."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


class SessionError(Exception):
    """Raised for session-related errors."""


_DEFAULT_TTL = 900  # 15 minutes


@dataclass
class SessionEntry:
    password: str
    expires_at: float  # Unix timestamp

    def is_expired(self) -> bool:
        return time.time() >= self.expires_at

    def seconds_remaining(self) -> float:
        return max(0.0, self.expires_at - time.time())


class SessionStore:
    """In-process password cache keyed by vault path."""

    def __init__(self) -> None:
        self._cache: dict[str, SessionEntry] = {}

    def set(self, vault_path: Path, password: str, ttl: int = _DEFAULT_TTL) -> SessionEntry:
        """Cache *password* for *vault_path* for *ttl* seconds."""
        if ttl <= 0:
            raise SessionError("TTL must be a positive integer.")
        entry = SessionEntry(
            password=password,
            expires_at=time.time() + ttl,
        )
        self._cache[str(vault_path.resolve())] = entry
        return entry

    def get(self, vault_path: Path) -> Optional[str]:
        """Return the cached password or *None* if absent / expired."""
        key = str(vault_path.resolve())
        entry = self._cache.get(key)
        if entry is None:
            return None
        if entry.is_expired():
            del self._cache[key]
            return None
        return entry.password

    def clear(self, vault_path: Path) -> bool:
        """Remove the cached entry for *vault_path*. Returns True if it existed."""
        key = str(vault_path.resolve())
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear_all(self) -> int:
        """Remove all cached entries. Returns the number of entries cleared."""
        count = len(self._cache)
        self._cache.clear()
        return count

    def status(self, vault_path: Path) -> Optional[SessionEntry]:
        """Return the live *SessionEntry* or None."""
        key = str(vault_path.resolve())
        entry = self._cache.get(key)
        if entry is None or entry.is_expired():
            return None
        return entry


# Module-level singleton used by CLI commands.
_session_store = SessionStore()


def get_store() -> SessionStore:
    return _session_store
