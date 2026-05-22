"""Tests for envault.env_clone."""
from __future__ import annotations

from pathlib import Path

import pytest

from envault.env_clone import CloneError, clone_vault, clone_vault_file
from envault.vault import Vault, VaultNotFoundError

PASSWORD = "test-secret"


@pytest.fixture()
def src_vault(tmp_path: Path) -> Path:
    vp = tmp_path / "src.vault"
    v = Vault(vp, PASSWORD)
    v.set("KEY_A", "alpha")
    v.set("KEY_B", "beta")
    v.set("KEY_C", "gamma")
    return vp


def test_clone_all_entries(src_vault: Path, tmp_path: Path) -> None:
    dst = tmp_path / "dst.vault"
    count = clone_vault(src_vault, dst, PASSWORD)
    assert count == 3
    v = Vault(dst, PASSWORD)
    assert v.get("KEY_A") == "alpha"
    assert v.get("KEY_B") == "beta"
    assert v.get("KEY_C") == "gamma"


def test_clone_selected_keys(src_vault: Path, tmp_path: Path) -> None:
    dst = tmp_path / "dst.vault"
    count = clone_vault(src_vault, dst, PASSWORD, keys=["KEY_A", "KEY_C"])
    assert count == 2
    v = Vault(dst, PASSWORD)
    assert v.get("KEY_A") == "alpha"
    assert v.get("KEY_B") is None
    assert v.get("KEY_C") == "gamma"


def test_clone_missing_source_raises(tmp_path: Path) -> None:
    with pytest.raises(VaultNotFoundError):
        clone_vault(tmp_path / "nope.vault", tmp_path / "dst.vault", PASSWORD)


def test_clone_existing_dst_raises_without_overwrite(
    src_vault: Path, tmp_path: Path
) -> None:
    dst = tmp_path / "dst.vault"
    dst.write_bytes(b"existing")
    with pytest.raises(CloneError, match="already exists"):
        clone_vault(src_vault, dst, PASSWORD)


def test_clone_overwrite_replaces_destination(
    src_vault: Path, tmp_path: Path
) -> None:
    dst = tmp_path / "dst.vault"
    # First clone
    clone_vault(src_vault, dst, PASSWORD)
    # Overwrite with only one key
    count = clone_vault(src_vault, dst, PASSWORD, keys=["KEY_B"], overwrite=True)
    assert count == 1
    v = Vault(dst, PASSWORD)
    assert v.get("KEY_A") is None
    assert v.get("KEY_B") == "beta"


def test_clone_nonexistent_keys_ignored(src_vault: Path, tmp_path: Path) -> None:
    dst = tmp_path / "dst.vault"
    count = clone_vault(src_vault, dst, PASSWORD, keys=["KEY_A", "MISSING"])
    assert count == 1


def test_clone_vault_file_copies_bytes(src_vault: Path, tmp_path: Path) -> None:
    dst = tmp_path / "dst.vault"
    clone_vault_file(src_vault, dst)
    assert dst.read_bytes() == src_vault.read_bytes()


def test_clone_vault_file_missing_src_raises(tmp_path: Path) -> None:
    with pytest.raises(VaultNotFoundError):
        clone_vault_file(tmp_path / "nope.vault", tmp_path / "dst.vault")


def test_clone_vault_file_no_overwrite_raises(src_vault: Path, tmp_path: Path) -> None:
    dst = tmp_path / "dst.vault"
    dst.write_bytes(b"x")
    with pytest.raises(CloneError):
        clone_vault_file(src_vault, dst)


def test_clone_vault_file_overwrite(src_vault: Path, tmp_path: Path) -> None:
    dst = tmp_path / "dst.vault"
    dst.write_bytes(b"old")
    clone_vault_file(src_vault, dst, overwrite=True)
    assert dst.read_bytes() == src_vault.read_bytes()
