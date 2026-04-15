"""Watch vault keys for changes and trigger callbacks or notifications."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional


class WatchError(Exception):
    """Raised when a watch operation fails."""


@dataclass
class WatchEntry:
    key: str
    last_value: Optional[str]
    callback_label: str
    created_at: str

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "last_value": self.last_value,
            "callback_label": self.callback_label,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WatchEntry":
        return cls(
            key=data["key"],
            last_value=data.get("last_value"),
            callback_label=data["callback_label"],
            created_at=data["created_at"],
        )


def _watch_path(vault_path: Path) -> Path:
    return vault_path.parent / (vault_path.stem + ".watches.json")


def _load(path: Path) -> Dict[str, dict]:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save(path: Path, data: Dict[str, dict]) -> None:
    path.write_text(json.dumps(data, indent=2))


def add_watch(vault_path: Path, key: str, callback_label: str, current_value: Optional[str] = None) -> WatchEntry:
    """Register a watch on a vault key."""
    from datetime import datetime, timezone
    path = _watch_path(vault_path)
    data = _load(path)
    if key in data:
        raise WatchError(f"Key '{key}' is already being watched.")
    entry = WatchEntry(
        key=key,
        last_value=current_value,
        callback_label=callback_label,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    data[key] = entry.to_dict()
    _save(path, data)
    return entry


def remove_watch(vault_path: Path, key: str) -> bool:
    """Remove a watch. Returns True if removed, False if not found."""
    path = _watch_path(vault_path)
    data = _load(path)
    if key not in data:
        return False
    del data[key]
    _save(path, data)
    return True


def list_watches(vault_path: Path) -> List[WatchEntry]:
    """Return all active watches for a vault."""
    path = _watch_path(vault_path)
    data = _load(path)
    return [WatchEntry.from_dict(v) for v in data.values()]


def check_watches(vault_path: Path, current_values: Dict[str, Optional[str]]) -> List[WatchEntry]:
    """Compare current values against watched last-known values. Returns changed entries and updates stored values."""
    path = _watch_path(vault_path)
    data = _load(path)
    changed: List[WatchEntry] = []
    for key, entry_dict in data.items():
        entry = WatchEntry.from_dict(entry_dict)
        new_val = current_values.get(key)
        if new_val != entry.last_value:
            entry.last_value = new_val
            data[key] = entry.to_dict()
            changed.append(entry)
    _save(path, data)
    return changed
