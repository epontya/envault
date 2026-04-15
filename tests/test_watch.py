"""Tests for envault.watch."""

from __future__ import annotations

from pathlib import Path

import pytest

from envault.watch import (
    WatchError,
    add_watch,
    check_watches,
    list_watches,
    remove_watch,
    _watch_path,
)


@pytest.fixture()
def vpath(tmp_path: Path) -> Path:
    p = tmp_path / "vault.env"
    p.write_text("{}")
    return p


def test_add_watch_creates_file(vpath: Path) -> None:
    add_watch(vpath, "DB_URL", "notify-slack", "postgres://localhost/db")
    assert _watch_path(vpath).exists()


def test_add_watch_returns_entry(vpath: Path) -> None:
    entry = add_watch(vpath, "API_KEY", "log", "secret")
    assert entry.key == "API_KEY"
    assert entry.callback_label == "log"
    assert entry.last_value == "secret"
    assert entry.created_at


def test_add_duplicate_raises(vpath: Path) -> None:
    add_watch(vpath, "KEY", "label", "v1")
    with pytest.raises(WatchError, match="already being watched"):
        add_watch(vpath, "KEY", "label2", "v2")


def test_remove_existing_returns_true(vpath: Path) -> None:
    add_watch(vpath, "TOKEN", "lbl", None)
    assert remove_watch(vpath, "TOKEN") is True


def test_remove_missing_returns_false(vpath: Path) -> None:
    assert remove_watch(vpath, "GHOST") is False


def test_list_watches_empty(vpath: Path) -> None:
    assert list_watches(vpath) == []


def test_list_watches_returns_all(vpath: Path) -> None:
    add_watch(vpath, "A", "la", "1")
    add_watch(vpath, "B", "lb", "2")
    entries = list_watches(vpath)
    keys = {e.key for e in entries}
    assert keys == {"A", "B"}


def test_check_watches_detects_change(vpath: Path) -> None:
    add_watch(vpath, "SECRET", "alert", "old_val")
    changed = check_watches(vpath, {"SECRET": "new_val"})
    assert len(changed) == 1
    assert changed[0].key == "SECRET"
    assert changed[0].last_value == "new_val"


def test_check_watches_no_change(vpath: Path) -> None:
    add_watch(vpath, "STABLE", "noop", "same")
    changed = check_watches(vpath, {"STABLE": "same"})
    assert changed == []


def test_check_watches_updates_stored_value(vpath: Path) -> None:
    add_watch(vpath, "VAR", "lbl", "v1")
    check_watches(vpath, {"VAR": "v2"})
    entries = list_watches(vpath)
    assert entries[0].last_value == "v2"


def test_check_watches_none_to_value(vpath: Path) -> None:
    add_watch(vpath, "NEW_KEY", "lbl", None)
    changed = check_watches(vpath, {"NEW_KEY": "appeared"})
    assert len(changed) == 1
