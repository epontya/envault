"""Tests for envault.rate_limit."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from envault.rate_limit import RateLimitError, RateLimitStore


@pytest.fixture
def store(tmp_path: Path) -> RateLimitStore:
    return RateLimitStore(tmp_path / "rate_limits.json")


def test_configure_creates_file(store: RateLimitStore, tmp_path: Path) -> None:
    store.configure("set", max_calls=5, window_seconds=60)
    assert (tmp_path / "rate_limits.json").exists()


def test_configure_returns_entry(store: RateLimitStore) -> None:
    entry = store.configure("get", max_calls=10, window_seconds=30)
    assert entry.operation == "get"
    assert entry.max_calls == 10
    assert entry.window_seconds == 30


def test_configure_invalid_max_calls_raises(store: RateLimitStore) -> None:
    with pytest.raises(RateLimitError, match="max_calls"):
        store.configure("set", max_calls=0, window_seconds=60)


def test_configure_invalid_window_raises(store: RateLimitStore) -> None:
    with pytest.raises(RateLimitError, match="window_seconds"):
        store.configure("set", max_calls=5, window_seconds=0)


def test_check_and_record_no_limit_returns_minus_one(store: RateLimitStore) -> None:
    result = store.check_and_record("unknown_op")
    assert result == -1


def test_check_and_record_within_limit(store: RateLimitStore) -> None:
    store.configure("set", max_calls=3, window_seconds=60)
    remaining = store.check_and_record("set")
    assert remaining == 2


def test_check_and_record_exceeds_limit_raises(store: RateLimitStore) -> None:
    store.configure("set", max_calls=2, window_seconds=60)
    store.check_and_record("set")
    store.check_and_record("set")
    with pytest.raises(RateLimitError, match="Rate limit exceeded"):
        store.check_and_record("set")


def test_timestamps_outside_window_are_pruned(store: RateLimitStore) -> None:
    store.configure("get", max_calls=2, window_seconds=1)
    store.check_and_record("get")
    store.check_and_record("get")
    time.sleep(1.1)
    # Window has passed — should not raise
    remaining = store.check_and_record("get")
    assert remaining == 1


def test_get_returns_none_for_missing(store: RateLimitStore) -> None:
    assert store.get("nonexistent") is None


def test_get_returns_entry(store: RateLimitStore) -> None:
    store.configure("delete", max_calls=1, window_seconds=10)
    entry = store.get("delete")
    assert entry is not None
    assert entry.max_calls == 1


def test_remove_existing_returns_true(store: RateLimitStore) -> None:
    store.configure("set", max_calls=5, window_seconds=60)
    assert store.remove("set") is True
    assert store.get("set") is None


def test_remove_missing_returns_false(store: RateLimitStore) -> None:
    assert store.remove("noop") is False


def test_list_operations_sorted(store: RateLimitStore) -> None:
    store.configure("set", max_calls=5, window_seconds=60)
    store.configure("get", max_calls=10, window_seconds=60)
    store.configure("delete", max_calls=2, window_seconds=60)
    assert store.list_operations() == ["delete", "get", "set"]


def test_persistence_across_instances(tmp_path: Path) -> None:
    path = tmp_path / "rl.json"
    s1 = RateLimitStore(path)
    s1.configure("rotate", max_calls=3, window_seconds=120)
    s2 = RateLimitStore(path)
    entry = s2.get("rotate")
    assert entry is not None
    assert entry.max_calls == 3
