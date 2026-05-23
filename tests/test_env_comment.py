"""Tests for envault.env_comment."""
from __future__ import annotations

import json

import pytest

from envault.env_comment import (
    CommentError,
    _comment_path,
    get_comment,
    list_comments,
    remove_comment,
    set_comment,
)


@pytest.fixture()
def vpath(tmp_path):
    return str(tmp_path / "my.vault")


def test_set_comment_creates_file(vpath):
    set_comment(vpath, "DB_HOST", "Primary database host")
    assert _comment_path(vpath).exists()


def test_set_comment_returns_comment(vpath):
    result = set_comment(vpath, "DB_HOST", "Primary database host")
    assert result == "Primary database host"


def test_get_comment_after_set(vpath):
    set_comment(vpath, "API_KEY", "Third-party API key")
    assert get_comment(vpath, "API_KEY") == "Third-party API key"


def test_get_comment_missing_key_returns_none(vpath):
    assert get_comment(vpath, "MISSING") is None


def test_get_comment_no_file_returns_none(vpath):
    assert get_comment(vpath, "ANY") is None


def test_set_comment_empty_key_raises(vpath):
    with pytest.raises(CommentError, match="empty"):
        set_comment(vpath, "", "some comment")


def test_overwrite_comment(vpath):
    set_comment(vpath, "PORT", "old comment")
    set_comment(vpath, "PORT", "new comment")
    assert get_comment(vpath, "PORT") == "new comment"


def test_remove_existing_returns_true(vpath):
    set_comment(vpath, "SECRET", "very secret")
    assert remove_comment(vpath, "SECRET") is True


def test_remove_deletes_entry(vpath):
    set_comment(vpath, "SECRET", "very secret")
    remove_comment(vpath, "SECRET")
    assert get_comment(vpath, "SECRET") is None


def test_remove_missing_returns_false(vpath):
    assert remove_comment(vpath, "NOPE") is False


def test_list_comments_empty_when_no_file(vpath):
    assert list_comments(vpath) == {}


def test_list_comments_returns_all(vpath):
    set_comment(vpath, "A", "alpha")
    set_comment(vpath, "B", "beta")
    result = list_comments(vpath)
    assert result == {"A": "alpha", "B": "beta"}


def test_comment_file_is_valid_json(vpath):
    set_comment(vpath, "X", "hello")
    raw = json.loads(_comment_path(vpath).read_text())
    assert raw["X"] == "hello"
