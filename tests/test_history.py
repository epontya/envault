"""Tests for envault.history."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from envault.history import HistoryEntry, HistoryError, HistoryStore


@pytest.fixture()
def store(tmp_path: Path) -> HistoryStore:
    return HistoryStore(tmp_path / "test.history.json")


def test_record_creates_file(store: HistoryStore, tmp_path: Path):
    store.record("API_KEY", "abc123")
    assert (tmp_path / "test.history.json").exists()


def test_record_returns_entry(store: HistoryStore):
    entry = store.record("DB_URL", "postgres://localhost")
    assert isinstance(entry, HistoryEntry)
    assert entry.key == "DB_URL"
    assert entry.value == "postgres://localhost"
    assert entry.action == "set"


def test_record_timestamp_is_recent(store: HistoryStore):
    before = time.time()
    entry = store.record("KEY", "val")
    after = time.time()
    assert before <= entry.timestamp <= after


def test_get_returns_only_matching_key(store: HistoryStore):
    store.record("A", "1")
    store.record("B", "2")
    store.record("A", "3")
    entries = store.get("A")
    assert len(entries) == 2
    assert all(e.key == "A" for e in entries)


def test_get_missing_key_returns_empty(store: HistoryStore):
    assert store.get("NONEXISTENT") == []


def test_all_returns_all_entries(store: HistoryStore):
    store.record("X", "1")
    store.record("Y", "2")
    store.record("Z", "3")
    assert len(store.all()) == 3


def test_delete_action_stored(store: HistoryStore):
    entry = store.record("MY_KEY", None, action="delete")
    assert entry.action == "delete"
    assert entry.value is None
    fetched = store.get("MY_KEY")
    assert fetched[0].action == "delete"


def test_invalid_action_raises(store: HistoryStore):
    with pytest.raises(HistoryError, match="Invalid action"):
        store.record("K", "v", action="update")


def test_clear_specific_key(store: HistoryStore):
    store.record("A", "1")
    store.record("B", "2")
    store.record("A", "3")
    removed = store.clear("A")
    assert removed == 2
    assert store.get("A") == []
    assert len(store.get("B")) == 1


def test_clear_all(store: HistoryStore):
    store.record("A", "1")
    store.record("B", "2")
    removed = store.clear()
    assert removed == 2
    assert store.all() == []


def test_multiple_records_appended(store: HistoryStore):
    for i in range(5):
        store.record("KEY", str(i))
    assert len(store.get("KEY")) == 5
