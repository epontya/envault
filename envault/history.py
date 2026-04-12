"""Track value change history for vault entries."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import List, Optional


class HistoryError(Exception):
    """Raised when history operations fail."""


class HistoryEntry:
    __slots__ = ("key", "value", "timestamp", "action")

    def __init__(self, key: str, value: Optional[str], timestamp: float, action: str):
        self.key = key
        self.value = value
        self.timestamp = timestamp
        self.action = action  # 'set' | 'delete'

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "value": self.value,
            "timestamp": self.timestamp,
            "action": self.action,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "HistoryEntry":
        return cls(
            key=d["key"],
            value=d.get("value"),
            timestamp=float(d["timestamp"]),
            action=d["action"],
        )


class HistoryStore:
    def __init__(self, history_path: Path):
        self._path = history_path

    def _load(self) -> List[dict]:
        if not self._path.exists():
            return []
        try:
            return json.loads(self._path.read_text())
        except (json.JSONDecodeError, OSError) as exc:
            raise HistoryError(f"Failed to read history: {exc}") from exc

    def _save(self, records: List[dict]) -> None:
        try:
            self._path.write_text(json.dumps(records, indent=2))
        except OSError as exc:
            raise HistoryError(f"Failed to write history: {exc}") from exc

    def record(self, key: str, value: Optional[str], action: str = "set") -> HistoryEntry:
        if action not in ("set", "delete"):
            raise HistoryError(f"Invalid action: {action!r}")
        entry = HistoryEntry(key=key, value=value, timestamp=time.time(), action=action)
        records = self._load()
        records.append(entry.to_dict())
        self._save(records)
        return entry

    def get(self, key: str) -> List[HistoryEntry]:
        return [
            HistoryEntry.from_dict(r)
            for r in self._load()
            if r["key"] == key
        ]

    def all(self) -> List[HistoryEntry]:
        return [HistoryEntry.from_dict(r) for r in self._load()]

    def clear(self, key: Optional[str] = None) -> int:
        records = self._load()
        if key is None:
            removed = len(records)
            self._save([])
        else:
            kept = [r for r in records if r["key"] != key]
            removed = len(records) - len(kept)
            self._save(kept)
        return removed
