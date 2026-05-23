"""Tests for envault.env_readonly."""
from __future__ import annotations

import pytest

from envault.env_readonly import (
    ReadOnlyError,
    protect,
    unprotect,
    is_protected,
    list_protected,
    assert_writable,
)


@pytest.fixture
def vpath(tmp_path) -> str:
    return str(tmp_path / "test.vault")


def test_protect_creates_file(vpath, tmp_path):
    protect(vpath, "API_KEY")
    files = list(tmp_path.iterdir())
    assert any(".readonly.json" in f.name for f in files)


def test_protect_returns_sorted_keys(vpath):
    result = protect(vpath, "Z_KEY")
    protect(vpath, "A_KEY")
    result2 = protect(vpath, "M_KEY")
    assert result2 == ["A_KEY", "M_KEY", "Z_KEY"]


def test_protect_empty_key_raises(vpath):
    with pytest.raises(ReadOnlyError):
        protect(vpath, "")


def test_duplicate_protect_not_duplicated(vpath):
    protect(vpath, "KEY")
    result = protect(vpath, "KEY")
    assert result.count("KEY") == 1


def test_is_protected_true_after_protect(vpath):
    protect(vpath, "SECRET")
    assert is_protected(vpath, "SECRET") is True


def test_is_protected_false_before_protect(vpath):
    assert is_protected(vpath, "MISSING") is False


def test_unprotect_existing_returns_true(vpath):
    protect(vpath, "KEY")
    assert unprotect(vpath, "KEY") is True


def test_unprotect_missing_returns_false(vpath):
    assert unprotect(vpath, "GHOST") is False


def test_unprotect_removes_from_list(vpath):
    protect(vpath, "A")
    protect(vpath, "B")
    unprotect(vpath, "A")
    assert "A" not in list_protected(vpath)
    assert "B" in list_protected(vpath)


def test_list_protected_empty_when_no_file(vpath):
    assert list_protected(vpath) == []


def test_list_protected_sorted(vpath):
    protect(vpath, "Z")
    protect(vpath, "A")
    protect(vpath, "M")
    assert list_protected(vpath) == ["A", "M", "Z"]


def test_assert_writable_raises_when_protected(vpath):
    protect(vpath, "LOCKED")
    with pytest.raises(ReadOnlyError, match="LOCKED"):
        assert_writable(vpath, "LOCKED")


def test_assert_writable_passes_when_not_protected(vpath):
    assert_writable(vpath, "FREE")  # should not raise
