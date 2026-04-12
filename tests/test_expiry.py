"""Tests for envault.expiry."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from envault.expiry import ExpiryError, ExpiryStore


@pytest.fixture()
def store(tmp_path: Path) -> ExpiryStore:
    return ExpiryStore(tmp_path / "expiry.json")


def _future(seconds: int = 3600) -> datetime:
    return datetime.now(timezone.utc) + timedelta(seconds=seconds)


def _past(seconds: int = 3600) -> datetime:
    return datetime.now(timezone.utc) - timedelta(seconds=seconds)


def test_set_expiry_creates_file(store: ExpiryStore, tmp_path: Path) -> None:
    store.set_expiry("MY_KEY", _future())
    assert (tmp_path / "expiry.json").exists()


def test_set_expiry_returns_utc_datetime(store: ExpiryStore) -> None:
    dt = _future()
    result = store.set_expiry("K", dt)
    assert result.tzinfo == timezone.utc


def test_set_expiry_naive_raises(store: ExpiryStore) -> None:
    naive = datetime(2030, 1, 1)  # no tzinfo
    with pytest.raises(ExpiryError):
        store.set_expiry("K", naive)


def test_get_expiry_returns_none_when_not_set(store: ExpiryStore) -> None:
    assert store.get_expiry("MISSING") is None


def test_get_expiry_round_trip(store: ExpiryStore) -> None:
    dt = _future()
    store.set_expiry("K", dt)
    got = store.get_expiry("K")
    assert got is not None
    assert abs((got - dt).total_seconds()) < 1


def test_is_expired_false_for_future(store: ExpiryStore) -> None:
    store.set_expiry("K", _future())
    assert store.is_expired("K") is False


def test_is_expired_true_for_past(store: ExpiryStore) -> None:
    store.set_expiry("K", _past())
    assert store.is_expired("K") is True


def test_is_expired_false_when_no_expiry(store: ExpiryStore) -> None:
    assert store.is_expired("UNSET") is False


def test_remove_existing_key(store: ExpiryStore) -> None:
    store.set_expiry("K", _future())
    assert store.remove("K") is True
    assert store.get_expiry("K") is None


def test_remove_missing_key_returns_false(store: ExpiryStore) -> None:
    assert store.remove("NOPE") is False


def test_all_expired_returns_only_expired(store: ExpiryStore) -> None:
    store.set_expiry("OLD", _past())
    store.set_expiry("NEW", _future())
    expired = store.all_expired()
    assert "OLD" in expired
    assert "NEW" not in expired


def test_list_all_returns_all_keys(store: ExpiryStore) -> None:
    store.set_expiry("A", _future(100))
    store.set_expiry("B", _future(200))
    listing = store.list_all()
    assert set(listing.keys()) == {"A", "B"}


def test_persistence_across_instances(tmp_path: Path) -> None:
    path = tmp_path / "expiry.json"
    dt = _future()
    ExpiryStore(path).set_expiry("PERSIST", dt)
    got = ExpiryStore(path).get_expiry("PERSIST")
    assert got is not None
    assert abs((got - dt).total_seconds()) < 1
