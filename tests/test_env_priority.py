"""Tests for envault.env_priority."""
import pytest

from envault.env_priority import (
    PriorityError,
    _priority_path,
    get_priority,
    list_by_priority,
    remove_priority,
    set_priority,
)


@pytest.fixture()
def vpath(tmp_path):
    return tmp_path / "vault.db"


def test_set_priority_creates_file(vpath):
    set_priority(vpath, "API_KEY", "high")
    assert _priority_path(vpath).exists()


def test_set_priority_returns_level(vpath):
    result = set_priority(vpath, "DB_PASS", "critical")
    assert result == "critical"


def test_get_priority_after_set(vpath):
    set_priority(vpath, "TOKEN", "normal")
    assert get_priority(vpath, "TOKEN") == "normal"


def test_get_priority_missing_key_returns_none(vpath):
    assert get_priority(vpath, "MISSING") is None


def test_set_priority_empty_key_raises(vpath):
    with pytest.raises(PriorityError, match="empty"):
        set_priority(vpath, "", "low")


def test_set_priority_invalid_level_raises(vpath):
    with pytest.raises(PriorityError, match="Invalid priority"):
        set_priority(vpath, "KEY", "urgent")


def test_remove_existing_returns_true(vpath):
    set_priority(vpath, "KEY", "low")
    assert remove_priority(vpath, "KEY") is True


def test_remove_existing_clears_entry(vpath):
    set_priority(vpath, "KEY", "low")
    remove_priority(vpath, "KEY")
    assert get_priority(vpath, "KEY") is None


def test_remove_missing_returns_false(vpath):
    assert remove_priority(vpath, "GHOST") is False


def test_list_by_priority_all(vpath):
    set_priority(vpath, "A", "high")
    set_priority(vpath, "B", "low")
    data = list_by_priority(vpath)
    assert data == {"A": "high", "B": "low"}


def test_list_by_priority_filtered(vpath):
    set_priority(vpath, "A", "high")
    set_priority(vpath, "B", "low")
    set_priority(vpath, "C", "high")
    data = list_by_priority(vpath, "high")
    assert set(data.keys()) == {"A", "C"}
    assert all(v == "high" for v in data.values())


def test_list_by_priority_invalid_level_raises(vpath):
    with pytest.raises(PriorityError, match="Invalid priority"):
        list_by_priority(vpath, "extreme")


def test_list_by_priority_empty_vault_returns_empty(vpath):
    assert list_by_priority(vpath) == {}


def test_overwrite_priority(vpath):
    set_priority(vpath, "KEY", "low")
    set_priority(vpath, "KEY", "critical")
    assert get_priority(vpath, "KEY") == "critical"
