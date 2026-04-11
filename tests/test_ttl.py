"""Tests for envault.ttl module."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from envault.ttl import TTLEntry, TTLError, TTLStore


@pytest.fixture
def store(tmp_path: Path) -> TTLStore:
    return TTLStore(tmp_path / ".ttl.json")


def test_set_ttl_creates_file(store: TTLStore, tmp_path: Path) -> None:
    store.set_ttl("MY_KEY", 60)
    assert (tmp_path / ".ttl.json").exists()


def test_set_ttl_returns_entry(store: TTLStore) -> None:
    entry = store.set_ttl("MY_KEY", 30)
    assert entry.key == "MY_KEY"
    assert entry.expires_at > time.time()


def test_set_ttl_negative_raises(store: TTLStore) -> None:
    with pytest.raises(TTLError):
        store.set_ttl("KEY", -5)


def test_set_ttl_zero_raises(store: TTLStore) -> None:
    with pytest.raises(TTLError):
        store.set_ttl("KEY", 0)


def test_get_entry_returns_none_for_unknown(store: TTLStore) -> None:
    assert store.get_entry("MISSING") is None


def test_get_entry_after_set(store: TTLStore) -> None:
    store.set_ttl("FOO", 100)
    entry = store.get_entry("FOO")
    assert entry is not None
    assert entry.key == "FOO"


def test_is_expired_false_for_future(store: TTLStore) -> None:
    store.set_ttl("BAR", 9999)
    assert not store.is_expired("BAR")


def test_is_expired_true_for_past(store: TTLStore) -> None:
    store.set_ttl("OLD", 0.001)
    time.sleep(0.05)
    assert store.is_expired("OLD")


def test_is_expired_false_for_unknown_key(store: TTLStore) -> None:
    assert not store.is_expired("GHOST")


def test_remove_existing_key(store: TTLStore) -> None:
    store.set_ttl("DEL", 60)
    assert store.remove("DEL") is True
    assert store.get_entry("DEL") is None


def test_remove_missing_key_returns_false(store: TTLStore) -> None:
    assert store.remove("NOPE") is False


def test_purge_expired_returns_expired_keys(store: TTLStore) -> None:
    store.set_ttl("ALIVE", 9999)
    store.set_ttl("DEAD", 0.001)
    time.sleep(0.05)
    expired = store.purge_expired(["ALIVE", "DEAD"])
    assert expired == ["DEAD"]
    assert store.get_entry("DEAD") is None
    assert store.get_entry("ALIVE") is not None


def test_list_entries_sorted(store: TTLStore) -> None:
    store.set_ttl("Z_KEY", 100)
    store.set_ttl("A_KEY", 200)
    entries = store.list_entries()
    assert [e.key for e in entries] == ["A_KEY", "Z_KEY"]


def test_ttl_entry_seconds_remaining() -> None:
    entry = TTLEntry(key="K", expires_at=time.time() + 50)
    remaining = entry.seconds_remaining()
    assert 49 < remaining <= 50


def test_ttl_entry_seconds_remaining_expired() -> None:
    entry = TTLEntry(key="K", expires_at=time.time() - 10)
    assert entry.seconds_remaining() == 0.0
