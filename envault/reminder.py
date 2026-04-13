"""Reminder system: schedule reminders to rotate or review vault keys."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


class ReminderError(Exception):
    """Raised when a reminder operation fails."""


_REMINDER_FILE = ".envault_reminders.json"


def _reminder_path(vault_path: Path) -> Path:
    return vault_path.parent / _REMINDER_FILE


def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2))


def set_reminder(vault_path: Path, key: str, remind_at: datetime, note: str = "") -> dict:
    """Schedule a reminder for *key* at *remind_at* (UTC)."""
    if remind_at.tzinfo is None:
        raise ReminderError("remind_at must be timezone-aware (UTC recommended).")
    rpath = _reminder_path(vault_path)
    data = _load(rpath)
    entry = {
        "key": key,
        "remind_at": remind_at.isoformat(),
        "note": note,
    }
    data[key] = entry
    _save(rpath, data)
    return entry


def get_reminder(vault_path: Path, key: str) -> Optional[dict]:
    """Return the reminder entry for *key*, or None if not set."""
    data = _load(_reminder_path(vault_path))
    return data.get(key)


def remove_reminder(vault_path: Path, key: str) -> bool:
    """Remove reminder for *key*. Returns True if it existed."""
    rpath = _reminder_path(vault_path)
    data = _load(rpath)
    if key not in data:
        return False
    del data[key]
    _save(rpath, data)
    return True


def due_reminders(vault_path: Path, now: Optional[datetime] = None) -> list[dict]:
    """Return all reminders whose remind_at <= now (UTC)."""
    if now is None:
        now = datetime.now(timezone.utc)
    data = _load(_reminder_path(vault_path))
    result = []
    for entry in data.values():
        remind_at = datetime.fromisoformat(entry["remind_at"])
        if remind_at <= now:
            result.append(entry)
    result.sort(key=lambda e: e["remind_at"])
    return result


def list_reminders(vault_path: Path) -> list[dict]:
    """Return all reminders sorted by remind_at."""
    data = _load(_reminder_path(vault_path))
    entries = list(data.values())
    entries.sort(key=lambda e: e["remind_at"])
    return entries
