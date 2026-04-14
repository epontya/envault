"""Tests for envault.session."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from envault.session import SessionError, SessionStore


@pytest.fixture()
def store() -> SessionStore:
    return SessionStore()


@pytest.fixture()
def vpath(tmp_path: Path) -> Path:
    p = tmp_path / "test.vault"
    p.touch()
    return p


def test_set_and_get(store: SessionStore, vpath: Path) -> None:
    store.set(vpath, "s3cr3t", ttl=60)
    assert store.get(vpath) == "s3cr3t"


def test_get_missing_returns_none(store: SessionStore, vpath: Path) -> None:
    assert store.get(vpath) is None


def test_expired_entry_returns_none(store: SessionStore, vpath: Path) -> None:
    entry = store.set(vpath, "pw", ttl=1)
    # Manually expire the entry.
    entry.expires_at = time.time() - 1
    assert store.get(vpath) is None


def test_clear_existing_returns_true(store: SessionStore, vpath: Path) -> None:
    store.set(vpath, "pw", ttl=60)
    assert store.clear(vpath) is True
    assert store.get(vpath) is None


def test_clear_missing_returns_false(store: SessionStore, vpath: Path) -> None:
    assert store.clear(vpath) is False


def test_clear_all_returns_count(store: SessionStore, tmp_path: Path) -> None:
    for i in range(3):
        p = tmp_path / f"v{i}.vault"
        p.touch()
        store.set(p, f"pw{i}", ttl=60)
    assert store.clear_all() == 3


def test_zero_ttl_raises(store: SessionStore, vpath: Path) -> None:
    with pytest.raises(SessionError):
        store.set(vpath, "pw", ttl=0)


def test_negative_ttl_raises(store: SessionStore, vpath: Path) -> None:
    with pytest.raises(SessionError):
        store.set(vpath, "pw", ttl=-10)


def test_status_returns_entry_when_active(store: SessionStore, vpath: Path) -> None:
    store.set(vpath, "pw", ttl=60)
    entry = store.status(vpath)
    assert entry is not None
    assert entry.seconds_remaining() > 0


def test_status_returns_none_when_expired(store: SessionStore, vpath: Path) -> None:
    entry = store.set(vpath, "pw", ttl=1)
    entry.expires_at = time.time() - 1
    assert store.status(vpath) is None


def test_is_expired_false_for_fresh_entry(store: SessionStore, vpath: Path) -> None:
    entry = store.set(vpath, "pw", ttl=60)
    assert entry.is_expired() is False


def test_seconds_remaining_positive(store: SessionStore, vpath: Path) -> None:
    entry = store.set(vpath, "pw", ttl=120)
    assert entry.seconds_remaining() > 100
