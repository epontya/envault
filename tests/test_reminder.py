"""Tests for envault.reminder."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from envault.reminder import (
    ReminderError,
    due_reminders,
    get_reminder,
    list_reminders,
    remove_reminder,
    set_reminder,
)


@pytest.fixture()
def vpath(tmp_path: Path) -> Path:
    return tmp_path / ".envault"


def _future(days: int = 1) -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=days)


def _past(days: int = 1) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=days)


def test_set_reminder_returns_entry(vpath):
    entry = set_reminder(vpath, "API_KEY", _future(), note="rotate soon")
    assert entry["key"] == "API_KEY"
    assert "remind_at" in entry
    assert entry["note"] == "rotate soon"


def test_set_reminder_creates_file(vpath):
    set_reminder(vpath, "DB_PASS", _future())
    reminder_file = vpath.parent / ".envault_reminders.json"
    assert reminder_file.exists()


def test_get_reminder_returns_entry(vpath):
    set_reminder(vpath, "TOKEN", _future())
    entry = get_reminder(vpath, "TOKEN")
    assert entry is not None
    assert entry["key"] == "TOKEN"


def test_get_reminder_missing_returns_none(vpath):
    assert get_reminder(vpath, "MISSING") is None


def test_remove_existing_returns_true(vpath):
    set_reminder(vpath, "X", _future())
    assert remove_reminder(vpath, "X") is True
    assert get_reminder(vpath, "X") is None


def test_remove_missing_returns_false(vpath):
    assert remove_reminder(vpath, "GHOST") is False


def test_due_reminders_returns_past_entries(vpath):
    set_reminder(vpath, "OLD_KEY", _past())
    set_reminder(vpath, "FUTURE_KEY", _future())
    due = due_reminders(vpath)
    keys = [e["key"] for e in due]
    assert "OLD_KEY" in keys
    assert "FUTURE_KEY" not in keys


def test_due_reminders_empty_when_none_due(vpath):
    set_reminder(vpath, "SOON", _future(days=10))
    assert due_reminders(vpath) == []


def test_list_reminders_sorted(vpath):
    set_reminder(vpath, "B", _future(days=3))
    set_reminder(vpath, "A", _future(days=1))
    set_reminder(vpath, "C", _future(days=5))
    entries = list_reminders(vpath)
    keys = [e["key"] for e in entries]
    assert keys == ["A", "B", "C"]


def test_naive_datetime_raises(vpath):
    naive = datetime(2030, 1, 1)  # no tzinfo
    with pytest.raises(ReminderError):
        set_reminder(vpath, "K", naive)


def test_overwrite_reminder(vpath):
    dt1 = _future(days=1)
    dt2 = _future(days=5)
    set_reminder(vpath, "K", dt1, note="first")
    set_reminder(vpath, "K", dt2, note="second")
    entry = get_reminder(vpath, "K")
    assert entry["note"] == "second"
