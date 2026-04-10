"""Tests for envault.rotate."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.rotate import rotate_vault_password, RotationError
from envault.vault import Vault, VaultNotFoundError


@pytest.fixture()
def vault_file(tmp_path: Path) -> Path:
    path = tmp_path / ".envault"
    v = Vault(path, "old-secret")
    v.set("KEY1", "value1")
    v.set("KEY2", "value2")
    v.set("KEY3", "value3")
    return path


def test_rotate_returns_entry_count(vault_file: Path) -> None:
    count = rotate_vault_password(vault_file, "old-secret", "new-secret")
    assert count == 3


def test_rotate_new_password_can_read_values(vault_file: Path) -> None:
    rotate_vault_password(vault_file, "old-secret", "new-secret")
    new_vault = Vault(vault_file, "new-secret")
    assert new_vault.get("KEY1") == "value1"
    assert new_vault.get("KEY2") == "value2"
    assert new_vault.get("KEY3") == "value3"


def test_rotate_old_password_no_longer_works(vault_file: Path) -> None:
    rotate_vault_password(vault_file, "old-secret", "new-secret")
    old_vault = Vault(vault_file, "old-secret")
    with pytest.raises(ValueError):
        old_vault.get("KEY1")


def test_rotate_empty_vault_returns_zero(tmp_path: Path) -> None:
    path = tmp_path / ".envault"
    # Create an empty vault by setting and deleting a key
    v = Vault(path, "old-secret")
    count = rotate_vault_password(path, "old-secret", "new-secret")
    assert count == 0


def test_rotate_raises_for_missing_vault(tmp_path: Path) -> None:
    with pytest.raises(VaultNotFoundError):
        rotate_vault_password(tmp_path / "missing", "old", "new")


def test_rotate_raises_for_empty_old_password(vault_file: Path) -> None:
    with pytest.raises(ValueError, match="old_password"):
        rotate_vault_password(vault_file, "", "new-secret")


def test_rotate_raises_for_empty_new_password(vault_file: Path) -> None:
    with pytest.raises(ValueError, match="new_password"):
        rotate_vault_password(vault_file, "old-secret", "")


def test_rotate_raises_when_passwords_identical(vault_file: Path) -> None:
    with pytest.raises(RotationError, match="differ"):
        rotate_vault_password(vault_file, "same", "same")


def test_rotate_raises_for_wrong_old_password(vault_file: Path) -> None:
    with pytest.raises(RotationError, match="Failed to decrypt"):
        rotate_vault_password(vault_file, "wrong-password", "new-secret")
