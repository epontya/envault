"""Tests for envault.snapshot."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.vault import Vault
from envault.snapshot import (
    SnapshotError,
    save_snapshot,
    load_snapshot,
    restore_snapshot,
    list_snapshots,
    delete_snapshot,
)

PASSWORD = "test-password"


@pytest.fixture()
def vault(tmp_path: Path) -> Vault:
    v = Vault(tmp_path / "vault.db", PASSWORD)
    v.set("KEY1", "value1", PASSWORD)
    v.set("KEY2", "value2", PASSWORD)
    return v


@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    return tmp_path / "snapshots"


def test_save_snapshot_creates_file(vault, snap_dir):
    save_snapshot(vault, "snap1", snap_dir, PASSWORD)
    assert (snap_dir / "snap1.snap.json").exists()


def test_save_snapshot_payload_contains_entries(vault, snap_dir):
    payload = save_snapshot(vault, "snap1", snap_dir, PASSWORD)
    assert payload["entries"]["KEY1"] == "value1"
    assert payload["entries"]["KEY2"] == "value2"


def test_save_snapshot_duplicate_raises(vault, snap_dir):
    save_snapshot(vault, "snap1", snap_dir, PASSWORD)
    with pytest.raises(SnapshotError, match="already exists"):
        save_snapshot(vault, "snap1", snap_dir, PASSWORD)


def test_load_snapshot_returns_payload(vault, snap_dir):
    save_snapshot(vault, "snap1", snap_dir, PASSWORD)
    payload = load_snapshot("snap1", snap_dir)
    assert payload["name"] == "snap1"
    assert "created_at" in payload


def test_load_snapshot_missing_raises(snap_dir):
    with pytest.raises(SnapshotError, match="not found"):
        load_snapshot("ghost", snap_dir)


def test_restore_snapshot_populates_vault(vault, snap_dir, tmp_path):
    save_snapshot(vault, "snap1", snap_dir, PASSWORD)
    new_vault = Vault(tmp_path / "new_vault.db", PASSWORD)
    count = restore_snapshot(new_vault, "snap1", snap_dir, PASSWORD)
    assert count == 2
    assert new_vault.get("KEY1", PASSWORD) == "value1"


def test_restore_snapshot_no_overwrite(vault, snap_dir, tmp_path):
    save_snapshot(vault, "snap1", snap_dir, PASSWORD)
    new_vault = Vault(tmp_path / "new_vault.db", PASSWORD)
    new_vault.set("KEY1", "original", PASSWORD)
    restore_snapshot(new_vault, "snap1", snap_dir, PASSWORD, overwrite=False)
    assert new_vault.get("KEY1", PASSWORD) == "original"
    assert new_vault.get("KEY2", PASSWORD) == "value2"


def test_list_snapshots_sorted(vault, snap_dir):
    save_snapshot(vault, "beta", snap_dir, PASSWORD)
    save_snapshot(vault, "alpha", snap_dir, PASSWORD)
    assert list_snapshots(snap_dir) == ["alpha", "beta"]


def test_list_snapshots_empty_dir(snap_dir):
    assert list_snapshots(snap_dir) == []


def test_delete_snapshot_removes_file(vault, snap_dir):
    save_snapshot(vault, "snap1", snap_dir, PASSWORD)
    result = delete_snapshot("snap1", snap_dir)
    assert result is True
    assert not (snap_dir / "snap1.snap.json").exists()


def test_delete_snapshot_missing_returns_false(snap_dir):
    assert delete_snapshot("ghost", snap_dir) is False
