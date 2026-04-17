"""Tests for envault.env_encrypt_field."""
import pytest
from pathlib import Path
from envault.env_encrypt_field import (
    mark_sensitive,
    unmark_sensitive,
    is_sensitive,
    list_sensitive,
    _field_meta_path,
)


@pytest.fixture
def vpath(tmp_path):
    return tmp_path / "test.vault"


def test_mark_sensitive_creates_file(vpath):
    mark_sensitive(vpath, "SECRET_KEY")
    assert _field_meta_path(vpath).exists()


def test_is_sensitive_true_after_mark(vpath):
    mark_sensitive(vpath, "SECRET_KEY")
    assert is_sensitive(vpath, "SECRET_KEY") is True


def test_is_sensitive_false_before_mark(vpath):
    assert is_sensitive(vpath, "SOME_KEY") is False


def test_unmark_sensitive_returns_true_when_existed(vpath):
    mark_sensitive(vpath, "API_TOKEN")
    result = unmark_sensitive(vpath, "API_TOKEN")
    assert result is True


def test_unmark_sensitive_returns_false_when_missing(vpath):
    result = unmark_sensitive(vpath, "NONEXISTENT")
    assert result is False


def test_is_sensitive_false_after_unmark(vpath):
    mark_sensitive(vpath, "DB_PASS")
    unmark_sensitive(vpath, "DB_PASS")
    assert is_sensitive(vpath, "DB_PASS") is False


def test_list_sensitive_empty(vpath):
    assert list_sensitive(vpath) == []


def test_list_sensitive_multiple(vpath):
    mark_sensitive(vpath, "ZEBRA")
    mark_sensitive(vpath, "ALPHA")
    mark_sensitive(vpath, "MIDDLE")
    result = list_sensitive(vpath)
    assert result == ["ALPHA", "MIDDLE", "ZEBRA"]


def test_list_sensitive_excludes_unmarked(vpath):
    mark_sensitive(vpath, "KEY_A")
    mark_sensitive(vpath, "KEY_B")
    unmark_sensitive(vpath, "KEY_A")
    assert list_sensitive(vpath) == ["KEY_B"]


def test_mark_sensitive_idempotent(vpath):
    mark_sensitive(vpath, "TOKEN")
    mark_sensitive(vpath, "TOKEN")
    assert is_sensitive(vpath, "TOKEN") is True
    assert list_sensitive(vpath) == ["TOKEN"]
