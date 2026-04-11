"""TTL (time-to-live) support for vault entries."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional
import json


class TTLError(Exception):
    """Raised when a TTL operation fails."""


@dataclass
class TTLEntry:
    key: str
    expires_at: float  # Unix timestamp

    def is_expired(self) -> bool:
        return time.time() >= self.expires_at

    def seconds_remaining(self) -> float:
        return max(0.0, self.expires_at - time.time())


class TTLStore:
    """Persists per-key expiry metadata alongside a vault."""

    def __init__(self, ttl_path: Path) -> None:
        self._path = ttl_path
        self._data: Dict[str, float] = self._load()

    def _load(self) -> Dict[str, float]:
        if self._path.exists():
            try:
                return json.loads(self._path.read_text())
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    def _save(self) -> None:
        self._path.write_text(json.dumps(self._data, indent=2))

    def set_ttl(self, key: str, seconds: float) -> TTLEntry:
        if seconds <= 0:
            raise TTLError(f"TTL must be positive, got {seconds}")
        expires_at = time.time() + seconds
        self._data[key] = expires_at
        self._save()
        return TTLEntry(key=key, expires_at=expires_at)

    def get_entry(self, key: str) -> Optional[TTLEntry]:
        if key not in self._data:
            return None
        return TTLEntry(key=key, expires_at=self._data[key])

    def is_expired(self, key: str) -> bool:
        entry = self.get_entry(key)
        return entry.is_expired() if entry is not None else False

    def remove(self, key: str) -> bool:
        if key in self._data:
            del self._data[key]
            self._save()
            return True
        return False

    def purge_expired(self, vault_keys: list[str]) -> list[str]:
        """Remove expired keys from the vault key list and TTL store."""
        expired = [k for k in vault_keys if self.is_expired(k)]
        for k in expired:
            self.remove(k)
        return expired

    def list_entries(self) -> list[TTLEntry]:
        return [
            TTLEntry(key=k, expires_at=v)
            for k, v in sorted(self._data.items())
        ]
