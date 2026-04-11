"""Tests for envault.diff."""
from __future__ import annotations

import pytest

from envault.diff import diff_dicts, diff_snapshot_vs_vault, diff_two_snapshots, DiffResult
from envault.snapshot import save_snapshot
from envault.vault import Vault


PASSWORD = "test-pass"


@pytest.fixture()
def vault(tmp_path):
    v = Vault(str(tmp_path / "vault.db"), PASSWORD)
    v.set("KEY_A", "alpha", PASSWORD)
    v.set("KEY_B", "beta", PASSWORD)
    return v


@pytest.fixture()
def snap_dir(tmp_path):
    d = tmp_path / "snaps"
    d.mkdir()
    return str(d)


# --- diff_dicts ---

def test_diff_dicts_added():
    result = diff_dicts({"A": "1"}, {"A": "1", "B": "2"})
    assert result.added == {"B": "2"}
    assert not result.removed
    assert not result.changed


def test_diff_dicts_removed():
    result = diff_dicts({"A": "1", "B": "2"}, {"A": "1"})
    assert result.removed == {"B": "2"}
    assert not result.added
    assert not result.changed


def test_diff_dicts_changed():
    result = diff_dicts({"A": "old"}, {"A": "new"})
    assert result.changed == {"A": ("old", "new")}
    assert not result.added
    assert not result.removed


def test_diff_dicts_no_changes():
    result = diff_dicts({"A": "1"}, {"A": "1"})
    assert not result.has_changes


def test_diff_dicts_empty():
    result = diff_dicts({}, {})
    assert not result.has_changes


def test_summary_contains_symbols():
    result = DiffResult(
        added={"X": "1"},
        removed={"Y": "2"},
        changed={"Z": ("old", "new")},
    )
    s = result.summary()
    assert "+ X=1" in s
    assert "- Y=2" in s
    assert "~ Z" in s


def test_summary_no_changes():
    result = DiffResult()
    assert "(no changes)" in result.summary()


# --- diff_snapshot_vs_vault ---

def test_diff_snapshot_vs_vault_no_changes(vault, snap_dir):
    save_snapshot(vault, PASSWORD, "snap1", snap_dir=snap_dir)
    result = diff_snapshot_vs_vault(vault, PASSWORD, "snap1", snap_dir=snap_dir)
    assert not result.has_changes


def test_diff_snapshot_vs_vault_detects_added(vault, snap_dir):
    save_snapshot(vault, PASSWORD, "snap1", snap_dir=snap_dir)
    vault.set("KEY_C", "gamma", PASSWORD)
    result = diff_snapshot_vs_vault(vault, PASSWORD, "snap1", snap_dir=snap_dir)
    assert "KEY_C" in result.added


def test_diff_snapshot_vs_vault_detects_removed(vault, snap_dir):
    save_snapshot(vault, PASSWORD, "snap1", snap_dir=snap_dir)
    vault.delete("KEY_B", PASSWORD)
    result = diff_snapshot_vs_vault(vault, PASSWORD, "snap1", snap_dir=snap_dir)
    assert "KEY_B" in result.removed


def test_diff_snapshot_vs_vault_detects_changed(vault, snap_dir):
    save_snapshot(vault, PASSWORD, "snap1", snap_dir=snap_dir)
    vault.set("KEY_A", "changed", PASSWORD)
    result = diff_snapshot_vs_vault(vault, PASSWORD, "snap1", snap_dir=snap_dir)
    assert "KEY_A" in result.changed
    assert result.changed["KEY_A"] == ("alpha", "changed")


# --- diff_two_snapshots ---

def test_diff_two_snapshots_detects_change(vault, snap_dir):
    save_snapshot(vault, PASSWORD, "v1", snap_dir=snap_dir)
    vault.set("KEY_A", "updated", PASSWORD)
    save_snapshot(vault, PASSWORD, "v2", snap_dir=snap_dir)
    result = diff_two_snapshots(vault, PASSWORD, "v1", "v2", snap_dir=snap_dir)
    assert "KEY_A" in result.changed


def test_diff_two_snapshots_same(vault, snap_dir):
    save_snapshot(vault, PASSWORD, "v1", snap_dir=snap_dir)
    save_snapshot(vault, PASSWORD, "v2", snap_dir=snap_dir)
    result = diff_two_snapshots(vault, PASSWORD, "v1", "v2", snap_dir=snap_dir)
    assert not result.has_changes
