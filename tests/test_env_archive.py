"""Tests for envault.env_archive."""
from __future__ import annotations

import json
import time

import pytest

from envault.env_archive import (
    ArchiveError,
    _archive_path,
    archive_key,
    list_archived,
    purge_all,
    purge_key,
    restore_key,
)


@pytest.fixture()
def vpath(tmp_path):
    return tmp_path / "test.vault"


def test_archive_key_creates_file(vpath):
    archive_key(vpath, "MY_KEY", "secret")
    assert _archive_path(vpath).exists()


def test_archive_key_returns_entry(vpath):
    entry = archive_key(vpath, "DB_PASS", "hunter2")
    assert entry["key"] == "DB_PASS"
    assert entry["value"] == "hunter2"
    assert "archived_at" in entry


def test_archive_key_empty_key_raises(vpath):
    with pytest.raises(ArchiveError):
        archive_key(vpath, "", "value")


def test_list_archived_empty_when_no_file(vpath):
    assert list_archived(vpath) == []


def test_list_archived_returns_all_entries(vpath):
    archive_key(vpath, "KEY_A", "aaa")
    archive_key(vpath, "KEY_B", "bbb")
    entries = list_archived(vpath)
    keys = {e["key"] for e in entries}
    assert keys == {"KEY_A", "KEY_B"}


def test_list_archived_sorted_by_archived_at(vpath):
    archive_key(vpath, "FIRST", "1")
    time.sleep(0.01)
    archive_key(vpath, "SECOND", "2")
    entries = list_archived(vpath)
    assert entries[0]["key"] == "FIRST"
    assert entries[1]["key"] == "SECOND"


def test_restore_key_returns_value(vpath):
    archive_key(vpath, "TOKEN", "abc123")
    value = restore_key(vpath, "TOKEN")
    assert value == "abc123"


def test_restore_key_removes_from_archive(vpath):
    archive_key(vpath, "TOKEN", "abc123")
    restore_key(vpath, "TOKEN")
    assert list_archived(vpath) == []


def test_restore_key_missing_returns_none(vpath):
    assert restore_key(vpath, "GHOST") is None


def test_purge_key_returns_true_when_existed(vpath):
    archive_key(vpath, "OLD", "val")
    assert purge_key(vpath, "OLD") is True


def test_purge_key_returns_false_when_missing(vpath):
    assert purge_key(vpath, "NOPE") is False


def test_purge_key_removes_entry(vpath):
    archive_key(vpath, "GONE", "bye")
    purge_key(vpath, "GONE")
    assert list_archived(vpath) == []


def test_purge_all_returns_count(vpath):
    archive_key(vpath, "A", "1")
    archive_key(vpath, "B", "2")
    assert purge_all(vpath) == 2


def test_purge_all_clears_archive(vpath):
    archive_key(vpath, "X", "x")
    purge_all(vpath)
    assert list_archived(vpath) == []


def test_purge_all_empty_returns_zero(vpath):
    assert purge_all(vpath) == 0
