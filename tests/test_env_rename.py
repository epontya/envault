"""Tests for envault.env_rename."""

from __future__ import annotations

import pytest

from envault.vault import Vault
from envault.env_rename import RenameError, rename_key, bulk_rename


@pytest.fixture()
def vault(tmp_path):
    v = Vault(tmp_path / "vault.enc", password="secret")
    v.set("FOO", "foo_val")
    v.set("BAR", "bar_val")
    v.set("BAZ", "baz_val")
    return v


# ---------------------------------------------------------------------------
# rename_key
# ---------------------------------------------------------------------------

def test_rename_key_moves_value(vault):
    rename_key(vault, "FOO", "FOO_NEW")
    assert vault.get("FOO_NEW") == "foo_val"


def test_rename_key_removes_old_key(vault):
    rename_key(vault, "FOO", "FOO_NEW")
    assert vault.get("FOO") is None


def test_rename_key_missing_source_raises(vault):
    with pytest.raises(RenameError, match="Key not found"):
        rename_key(vault, "MISSING", "DEST")


def test_rename_key_same_name_raises(vault):
    with pytest.raises(RenameError, match="identical"):
        rename_key(vault, "FOO", "FOO")


def test_rename_key_dest_exists_no_overwrite_raises(vault):
    with pytest.raises(RenameError, match="already exists"):
        rename_key(vault, "FOO", "BAR")


def test_rename_key_dest_exists_overwrite_succeeds(vault):
    rename_key(vault, "FOO", "BAR", overwrite=True)
    assert vault.get("BAR") == "foo_val"
    assert vault.get("FOO") is None


# ---------------------------------------------------------------------------
# bulk_rename
# ---------------------------------------------------------------------------

def test_bulk_rename_returns_renamed_pairs(vault):
    result = bulk_rename(vault, {"FOO": "FOO2", "BAR": "BAR2"})
    assert ("FOO", "FOO2") in result
    assert ("BAR", "BAR2") in result


def test_bulk_rename_values_accessible(vault):
    bulk_rename(vault, {"FOO": "FOO2", "BAR": "BAR2"})
    assert vault.get("FOO2") == "foo_val"
    assert vault.get("BAR2") == "bar_val"


def test_bulk_rename_missing_key_raises_by_default(vault):
    with pytest.raises(RenameError, match="Key not found"):
        bulk_rename(vault, {"MISSING": "DEST"})


def test_bulk_rename_skip_missing_ignores_absent_keys(vault):
    result = bulk_rename(vault, {"MISSING": "DEST", "BAZ": "BAZ2"}, skip_missing=True)
    assert result == [("BAZ", "BAZ2")]


def test_bulk_rename_empty_mapping_returns_empty(vault):
    result = bulk_rename(vault, {})
    assert result == []


def test_bulk_rename_overwrite_flag_propagated(vault):
    # BAR already exists; without overwrite this should raise
    with pytest.raises(RenameError):
        bulk_rename(vault, {"FOO": "BAR"})

    # with overwrite it should succeed
    result = bulk_rename(vault, {"FOO": "BAR"}, overwrite=True)
    assert ("FOO", "BAR") in result
