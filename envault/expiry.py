"""Key expiry: set an absolute expiration date on vault entries."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


class ExpiryError(Exception):
    """Raised when an expiry operation fails."""


class ExpiryStore:
    """Persist and query per-key expiration timestamps."""

    def __init__(self, store_path: Path) -> None:
        self._path = store_path
        self._data: dict[str, str] = self._load()

    def _load(self) -> dict[str, str]:
        if self._path.exists():
            return json.loads(self._path.read_text())
        return {}

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._data, indent=2))

    def set_expiry(self, key: str, expires_at: datetime) -> datetime:
        """Set an absolute UTC expiration for *key*. Returns the stored timestamp."""
        if expires_at.tzinfo is None:
            raise ExpiryError("expires_at must be timezone-aware")
        utc = expires_at.astimezone(timezone.utc)
        self._data[key] = utc.isoformat()
        self._save()
        return utc

    def get_expiry(self, key: str) -> Optional[datetime]:
        """Return the UTC expiration datetime for *key*, or None if not set."""
        raw = self._data.get(key)
        if raw is None:
            return None
        return datetime.fromisoformat(raw)

    def is_expired(self, key: str) -> bool:
        """Return True if *key* has expired (or has no expiry set → False)."""
        exp = self.get_expiry(key)
        if exp is None:
            return False
        return datetime.now(timezone.utc) >= exp

    def remove(self, key: str) -> bool:
        """Remove the expiry for *key*. Returns True if it existed."""
        if key in self._data:
            del self._data[key]
            self._save()
            return True
        return False

    def all_expired(self) -> list[str]:
        """Return a list of all keys that are currently expired."""
        return [k for k in self._data if self.is_expired(k)]

    def list_all(self) -> dict[str, datetime]:
        """Return a mapping of key → expiry datetime for every tracked key."""
        return {k: datetime.fromisoformat(v) for k, v in self._data.items()}
