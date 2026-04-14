"""Rate limiting for vault operations — tracks and enforces per-operation call limits."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional


class RateLimitError(Exception):
    """Raised when a rate limit is exceeded."""


@dataclass
class RateLimitEntry:
    operation: str
    max_calls: int
    window_seconds: int
    timestamps: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "operation": self.operation,
            "max_calls": self.max_calls,
            "window_seconds": self.window_seconds,
            "timestamps": self.timestamps,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RateLimitEntry":
        return cls(
            operation=data["operation"],
            max_calls=data["max_calls"],
            window_seconds=data["window_seconds"],
            timestamps=data.get("timestamps", []),
        )


class RateLimitStore:
    def __init__(self, store_path: Path) -> None:
        self._path = store_path
        self._data: Dict[str, RateLimitEntry] = {}
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            raw = json.loads(self._path.read_text())
            self._data = {k: RateLimitEntry.from_dict(v) for k, v in raw.items()}

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps({k: v.to_dict() for k, v in self._data.items()}, indent=2))

    def configure(self, operation: str, max_calls: int, window_seconds: int) -> RateLimitEntry:
        if max_calls < 1:
            raise RateLimitError("max_calls must be >= 1")
        if window_seconds < 1:
            raise RateLimitError("window_seconds must be >= 1")
        entry = RateLimitEntry(operation=operation, max_calls=max_calls, window_seconds=window_seconds)
        self._data[operation] = entry
        self._save()
        return entry

    def check_and_record(self, operation: str) -> int:
        """Record a call and raise RateLimitError if limit exceeded. Returns remaining calls."""
        if operation not in self._data:
            return -1  # No limit configured
        entry = self._data[operation]
        now = time.time()
        cutoff = now - entry.window_seconds
        entry.timestamps = [t for t in entry.timestamps if t >= cutoff]
        if len(entry.timestamps) >= entry.max_calls:
            raise RateLimitError(
                f"Rate limit exceeded for '{operation}': "
                f"{entry.max_calls} calls per {entry.window_seconds}s"
            )
        entry.timestamps.append(now)
        self._save()
        return entry.max_calls - len(entry.timestamps)

    def get(self, operation: str) -> Optional[RateLimitEntry]:
        return self._data.get(operation)

    def remove(self, operation: str) -> bool:
        if operation not in self._data:
            return False
        del self._data[operation]
        self._save()
        return True

    def list_operations(self) -> list:
        return sorted(self._data.keys())
