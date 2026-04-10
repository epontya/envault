"""Tests for envault.sync."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envault.vault import Vault
from envault.sync import (
    SyncError,
    export_vault_data,
    import_vault_data,
    pull_from_file,
    push_to_file,
)

PASSWORD = "sync-secret"


@pytest.fixture()
def vault(tmp_path: Path) -> Vault:
    v = Vault(tmp_path / "test.vault", PASSWORD)
    v.set("KEY1", "value1")
    v.set("KEY2", "value2")
    return v


@pytest.fixture()
def empty_vault(tmp_path: Path) -> Vault:
    return Vault(tmp_path / "empty.vault", PASSWORD)


def test_export_vault_data(vault: Vault) -> None:
    data = export_vault_data(vault)
    assert data == {"KEY1": "value1", "KEY2": "value2"}


def test_import_vault_data_overwrites(empty_vault: Vault) -> None:
    written = import_vault_data(empty_vault, {"A": "1", "B": "2"})
    assert written == 2
    assert empty_vault.get("A") == "1"


def test_import_vault_data_no_overwrite(vault: Vault) -> None:
    written = import_vault_data(
        vault, {"KEY1": "NEW", "KEY3": "value3"}, overwrite=False
    )
    assert written == 1
    assert vault.get("KEY1") == "value1"  # unchanged
    assert vault.get("KEY3") == "value3"  # new key added


def test_push_and_pull_round_trip(tmp_path: Path, vault: Vault, empty_vault: Vault) -> None:
    sync_file = tmp_path / "vault.sync"
    push_to_file(vault, sync_file, PASSWORD)
    assert sync_file.exists()
    written = pull_from_file(empty_vault, sync_file, PASSWORD)
    assert written == 2
    assert empty_vault.get("KEY1") == "value1"
    assert empty_vault.get("KEY2") == "value2"


def test_pull_missing_file_raises(tmp_path: Path, empty_vault: Vault) -> None:
    with pytest.raises(SyncError, match="not found"):
        pull_from_file(empty_vault, tmp_path / "nonexistent.sync", PASSWORD)


def test_pull_wrong_password_raises(tmp_path: Path, vault: Vault, empty_vault: Vault) -> None:
    sync_file = tmp_path / "vault.sync"
    push_to_file(vault, sync_file, PASSWORD)
    with pytest.raises(SyncError, match="Failed to decrypt"):
        pull_from_file(empty_vault, sync_file, "wrong-password")


def test_pull_corrupted_file_raises(tmp_path: Path, empty_vault: Vault) -> None:
    from envault.crypto import encrypt

    bad_file = tmp_path / "bad.sync"
    # Valid encryption but not JSON inside
    bad_file.write_bytes(encrypt(PASSWORD, b"not-json-at-all"))
    with pytest.raises(SyncError, match="invalid JSON"):
        pull_from_file(empty_vault, bad_file, PASSWORD)
