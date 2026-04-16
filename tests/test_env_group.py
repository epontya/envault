"""Tests for envault.env_group."""
from __future__ import annotations
import pytest
from pathlib import Path
from envault.env_group import (
    GroupError, create_group, get_group, remove_group,
    list_groups, add_key_to_group, remove_key_from_group,
)


@pytest.fixture
def vpath(tmp_path) -> Path:
    return tmp_path / "vault.db"


def test_create_group_returns_keys(vpath):
    keys = create_group(vpath, "backend", ["DB_URL", "SECRET_KEY"])
    assert keys == ["DB_URL", "SECRET_KEY"]


def test_create_group_creates_file(vpath):
    create_group(vpath, "g", ["A"])
    assert vpath.with_suffix(".groups.json").exists()


def test_create_group_deduplicates_keys(vpath):
    keys = create_group(vpath, "g", ["A", "B", "A"])
    assert keys == ["A", "B"]


def test_create_group_empty_name_raises(vpath):
    with pytest.raises(GroupError):
        create_group(vpath, "", ["A"])


def test_create_group_empty_keys_raises(vpath):
    with pytest.raises(GroupError):
        create_group(vpath, "g", [])


def test_get_group_returns_keys(vpath):
    create_group(vpath, "g", ["X", "Y"])
    assert get_group(vpath, "g") == ["X", "Y"]


def test_get_missing_group_returns_none(vpath):
    assert get_group(vpath, "nope") is None


def test_remove_existing_group_returns_true(vpath):
    create_group(vpath, "g", ["A"])
    assert remove_group(vpath, "g") is True
    assert get_group(vpath, "g") is None


def test_remove_missing_group_returns_false(vpath):
    assert remove_group(vpath, "ghost") is False


def test_list_groups_empty(vpath):
    assert list_groups(vpath) == {}


def test_list_groups_returns_all(vpath):
    create_group(vpath, "a", ["K1"])
    create_group(vpath, "b", ["K2", "K3"])
    groups = list_groups(vpath)
    assert set(groups.keys()) == {"a", "b"}


def test_add_key_to_group(vpath):
    create_group(vpath, "g", ["A"])
    result = add_key_to_group(vpath, "g", "B")
    assert "B" in result


def test_add_duplicate_key_ignored(vpath):
    create_group(vpath, "g", ["A"])
    add_key_to_group(vpath, "g", "A")
    assert get_group(vpath, "g").count("A") == 1


def test_add_key_to_missing_group_raises(vpath):
    with pytest.raises(GroupError):
        add_key_to_group(vpath, "ghost", "K")


def test_remove_key_from_group(vpath):
    create_group(vpath, "g", ["A", "B"])
    assert remove_key_from_group(vpath, "g", "A") is True
    assert get_group(vpath, "g") == ["B"]


def test_remove_missing_key_returns_false(vpath):
    create_group(vpath, "g", ["A"])
    assert remove_key_from_group(vpath, "g", "Z") is False
