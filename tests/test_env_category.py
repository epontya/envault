"""Tests for envault.env_category."""
import pytest

from envault.env_category import (
    CategoryError,
    assign_category,
    get_category,
    list_by_category,
    list_categories,
    remove_category,
)


@pytest.fixture()
def vpath(tmp_path):
    return str(tmp_path / "test.vault")


def test_assign_category_creates_file(vpath, tmp_path):
    assign_category(vpath, "DB_HOST", "database")
    files = list(tmp_path.iterdir())
    assert any("categories" in f.name for f in files)


def test_assign_category_returns_name(vpath):
    result = assign_category(vpath, "DB_HOST", "database")
    assert result == "database"


def test_get_category_after_assign(vpath):
    assign_category(vpath, "API_KEY", "auth")
    assert get_category(vpath, "API_KEY") == "auth"


def test_get_category_missing_key_returns_none(vpath):
    assert get_category(vpath, "MISSING") is None


def test_assign_overwrites_existing(vpath):
    assign_category(vpath, "DB_HOST", "database")
    assign_category(vpath, "DB_HOST", "network")
    assert get_category(vpath, "DB_HOST") == "network"


def test_remove_existing_returns_true(vpath):
    assign_category(vpath, "X", "misc")
    assert remove_category(vpath, "X") is True


def test_remove_missing_returns_false(vpath):
    assert remove_category(vpath, "GHOST") is False


def test_remove_clears_key(vpath):
    assign_category(vpath, "X", "misc")
    remove_category(vpath, "X")
    assert get_category(vpath, "X") is None


def test_list_by_category_returns_matching_keys(vpath):
    assign_category(vpath, "DB_HOST", "database")
    assign_category(vpath, "DB_PORT", "database")
    assign_category(vpath, "API_KEY", "auth")
    keys = list_by_category(vpath, "database")
    assert keys == ["DB_HOST", "DB_PORT"]


def test_list_by_category_no_match_returns_empty(vpath):
    assign_category(vpath, "X", "misc")
    assert list_by_category(vpath, "nonexistent") == []


def test_list_categories_returns_distinct_sorted(vpath):
    assign_category(vpath, "A", "zebra")
    assign_category(vpath, "B", "alpha")
    assign_category(vpath, "C", "alpha")
    cats = list_categories(vpath)
    assert cats == ["alpha", "zebra"]


def test_list_categories_empty_vault(vpath):
    assert list_categories(vpath) == []


def test_assign_empty_key_raises(vpath):
    with pytest.raises(CategoryError):
        assign_category(vpath, "", "misc")


def test_assign_empty_category_raises(vpath):
    with pytest.raises(CategoryError):
        assign_category(vpath, "KEY", "")
