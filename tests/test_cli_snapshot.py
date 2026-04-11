"""Tests for envault.cli_snapshot."""

from __future__ import annotations

import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.vault import Vault
from envault.cli_snapshot import snapshot_group

PASSWORD = "cli-test-pass"


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_file(tmp_path: Path) -> Path:
    path = tmp_path / "vault.db"
    v = Vault(path, PASSWORD)
    v.set("FOO", "bar", PASSWORD)
    v.set("BAZ", "qux", PASSWORD)
    return path


@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    return tmp_path / "snaps"


def _invoke(runner, vault_file, snap_dir, *args):
    return runner.invoke(
        snapshot_group,
        [
            *args,
            "--vault-file", str(vault_file),
            "--snap-dir", str(snap_dir),
            "--password", PASSWORD,
        ],
    )


def test_save_success(runner, vault_file, snap_dir):
    result = _invoke(runner, vault_file, snap_dir, "save", "v1")
    assert result.exit_code == 0
    assert "saved" in result.output
    assert "2 key(s)" in result.output


def test_save_duplicate_fails(runner, vault_file, snap_dir):
    _invoke(runner, vault_file, snap_dir, "save", "v1")
    result = _invoke(runner, vault_file, snap_dir, "save", "v1")
    assert result.exit_code != 0
    assert "already exists" in result.output


def test_restore_success(runner, vault_file, snap_dir, tmp_path):
    _invoke(runner, vault_file, snap_dir, "save", "v1")
    new_vault_file = tmp_path / "new.db"
    result = runner.invoke(
        snapshot_group,
        [
            "restore", "v1",
            "--vault-file", str(new_vault_file),
            "--snap-dir", str(snap_dir),
            "--password", PASSWORD,
        ],
    )
    assert result.exit_code == 0
    assert "Restored 2" in result.output


def test_list_shows_names(runner, vault_file, snap_dir):
    _invoke(runner, vault_file, snap_dir, "save", "alpha")
    _invoke(runner, vault_file, snap_dir, "save", "beta")
    result = runner.invoke(
        snapshot_group, ["list", "--snap-dir", str(snap_dir)]
    )
    assert "alpha" in result.output
    assert "beta" in result.output


def test_list_empty(runner, snap_dir):
    result = runner.invoke(
        snapshot_group, ["list", "--snap-dir", str(snap_dir)]
    )
    assert "No snapshots found" in result.output


def test_delete_success(runner, vault_file, snap_dir):
    _invoke(runner, vault_file, snap_dir, "save", "v1")
    result = runner.invoke(
        snapshot_group, ["delete", "v1", "--snap-dir", str(snap_dir)]
    )
    assert result.exit_code == 0
    assert "deleted" in result.output


def test_delete_missing_fails(runner, snap_dir):
    result = runner.invoke(
        snapshot_group, ["delete", "ghost", "--snap-dir", str(snap_dir)]
    )
    assert result.exit_code != 0
    assert "not found" in result.output
