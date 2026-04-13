"""Tests for envault.backup."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from envault.backup import (
    BackupError,
    _backup_dir,
    create_backup,
    delete_backup,
    list_backups,
    restore_backup,
)


@pytest.fixture()
def vault_file(tmp_path: Path) -> Path:
    vf = tmp_path / "test.vault"
    vf.write_bytes(b"encrypted-content-v1")
    return vf


def test_create_backup_returns_entry(vault_file: Path) -> None:
    entry = create_backup(vault_file)
    assert "filename" in entry
    assert "created_at" in entry
    assert entry["label"] == ""


def test_create_backup_copies_file(vault_file: Path) -> None:
    entry = create_backup(vault_file)
    backup_dir = _backup_dir(vault_file)
    assert (backup_dir / entry["filename"]).read_bytes() == b"encrypted-content-v1"


def test_create_backup_with_label(vault_file: Path) -> None:
    entry = create_backup(vault_file, label="before-migration")
    assert entry["label"] == "before-migration"


def test_create_backup_missing_vault_raises(tmp_path: Path) -> None:
    with pytest.raises(BackupError, match="not found"):
        create_backup(tmp_path / "ghost.vault")


def test_list_backups_newest_first(vault_file: Path) -> None:
    create_backup(vault_file, label="first")
    time.sleep(0.01)
    vault_file.write_bytes(b"encrypted-content-v2")
    create_backup(vault_file, label="second")
    backups = list_backups(vault_file)
    assert len(backups) == 2
    assert backups[0]["label"] == "second"
    assert backups[1]["label"] == "first"


def test_list_backups_empty_when_none(vault_file: Path) -> None:
    assert list_backups(vault_file) == []


def test_restore_backup_overwrites_vault(vault_file: Path) -> None:
    entry = create_backup(vault_file)
    vault_file.write_bytes(b"corrupted")
    restore_backup(vault_file, entry["filename"])
    assert vault_file.read_bytes() == b"encrypted-content-v1"


def test_restore_missing_backup_raises(vault_file: Path) -> None:
    with pytest.raises(BackupError, match="not found"):
        restore_backup(vault_file, "nonexistent.vault")


def test_delete_backup_removes_file(vault_file: Path) -> None:
    entry = create_backup(vault_file)
    backup_dir = _backup_dir(vault_file)
    delete_backup(vault_file, entry["filename"])
    assert not (backup_dir / entry["filename"]).exists()


def test_delete_backup_removes_from_manifest(vault_file: Path) -> None:
    entry = create_backup(vault_file)
    delete_backup(vault_file, entry["filename"])
    assert list_backups(vault_file) == []


def test_delete_missing_backup_raises(vault_file: Path) -> None:
    with pytest.raises(BackupError, match="not found"):
        delete_backup(vault_file, "ghost.vault")
