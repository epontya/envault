"""Unit tests for envault.tags.TagStore."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.tags import TagStore


@pytest.fixture
def store(tmp_path: Path) -> TagStore:
    return TagStore(tmp_path / "tags.json")


def test_add_tag_creates_file(store: TagStore, tmp_path: Path) -> None:
    store.add("DB_URL", "database")
    assert (tmp_path / "tags.json").exists()


def test_add_and_get(store: TagStore) -> None:
    store.add("DB_URL", "database")
    store.add("DB_URL", "prod")
    assert set(store.get("DB_URL")) == {"database", "prod"}


def test_duplicate_tag_ignored(store: TagStore) -> None:
    store.add("KEY", "env")
    store.add("KEY", "env")
    assert store.get("KEY") == ["env"]


def test_get_missing_key_returns_empty(store: TagStore) -> None:
    assert store.get("NONEXISTENT") == []


def test_remove_existing_tag(store: TagStore) -> None:
    store.add("API_KEY", "secret")
    result = store.remove("API_KEY", "secret")
    assert result is True
    assert store.get("API_KEY") == []


def test_remove_last_tag_cleans_key(store: TagStore) -> None:
    store.add("API_KEY", "secret")
    store.remove("API_KEY", "secret")
    assert store.keys_for_tag("secret") == []


def test_remove_missing_tag_returns_false(store: TagStore) -> None:
    result = store.remove("MISSING", "nope")
    assert result is False


def test_keys_for_tag(store: TagStore) -> None:
    store.add("DB_URL", "prod")
    store.add("API_KEY", "prod")
    store.add("SECRET", "dev")
    assert store.keys_for_tag("prod") == ["API_KEY", "DB_URL"]


def test_keys_for_tag_no_match(store: TagStore) -> None:
    assert store.keys_for_tag("ghost") == []


def test_clear_key(store: TagStore) -> None:
    store.add("KEY", "a")
    store.add("KEY", "b")
    store.clear_key("KEY")
    assert store.get("KEY") == []


def test_all_tags(store: TagStore) -> None:
    store.add("A", "prod")
    store.add("B", "prod")
    store.add("C", "dev")
    assert store.all_tags() == ["dev", "prod"]


def test_all_tags_empty(store: TagStore) -> None:
    assert store.all_tags() == []


def test_persistence(tmp_path: Path) -> None:
    path = tmp_path / "tags.json"
    s1 = TagStore(path)
    s1.add("X", "alpha")
    s2 = TagStore(path)
    assert s2.get("X") == ["alpha"]
