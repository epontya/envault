"""CLI tests for the backup command group."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.backup import create_backup
from envault.cli_backup import backup_group


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def vault_file(tmp_path: Path) -> Path:
    vf = tmp_path / "my.vault"
    vf.write_bytes(b"secret-data")
    return vf


def _invoke(runner: CliRunner, vault_file: Path, *args: str):
    return runner.invoke(backup_group, [*args, str(vault_file)])


def test_create_success(runner: CliRunner, vault_file: Path) -> None:
    result = runner.invoke(backup_group, ["create", str(vault_file)])
    assert result.exit_code == 0
    assert "Backup created" in result.output


def test_create_with_label(runner: CliRunner, vault_file: Path) -> None:
    result = runner.invoke(backup_group, ["create", str(vault_file), "--label", "v1"])
    assert result.exit_code == 0
    assert "Label: v1" in result.output


def test_create_missing_vault_exits_nonzero(runner: CliRunner, tmp_path: Path) -> None:
    result = runner.invoke(backup_group, ["create", str(tmp_path / "ghost.vault")])
    assert result.exit_code != 0


def test_list_shows_backups(runner: CliRunner, vault_file: Path) -> None:
    create_backup(vault_file, label="snap1")
    result = runner.invoke(backup_group, ["list", str(vault_file)])
    assert result.exit_code == 0
    assert "snap1" in result.output


def test_list_empty_message(runner: CliRunner, vault_file: Path) -> None:
    result = runner.invoke(backup_group, ["list", str(vault_file)])
    assert result.exit_code == 0
    assert "No backups found" in result.output


def test_restore_success(runner: CliRunner, vault_file: Path) -> None:
    entry = create_backup(vault_file)
    vault_file.write_bytes(b"corrupted")
    result = runner.invoke(backup_group, ["restore", str(vault_file), entry["filename"]])
    assert result.exit_code == 0
    assert "restored" in result.output
    assert vault_file.read_bytes() == b"secret-data"


def test_restore_missing_exits_nonzero(runner: CliRunner, vault_file: Path) -> None:
    result = runner.invoke(backup_group, ["restore", str(vault_file), "ghost.vault"])
    assert result.exit_code != 0


def test_delete_success(runner: CliRunner, vault_file: Path) -> None:
    entry = create_backup(vault_file)
    result = runner.invoke(backup_group, ["delete", str(vault_file), entry["filename"]])
    assert result.exit_code == 0
    assert "deleted" in result.output


def test_delete_missing_exits_nonzero(runner: CliRunner, vault_file: Path) -> None:
    result = runner.invoke(backup_group, ["delete", str(vault_file), "ghost.vault"])
    assert result.exit_code != 0
