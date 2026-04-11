"""Tests for envault.copy (copy_entries / move_entries)."""

from __future__ import annotations

from pathlib import Path

import pytest

from envault.copy import CopyError, copy_entries, move_entries
from envault.vault import Vault, VaultNotFoundError

PASSWORD = "test-password"


@pytest.fixture()
def src_vault(tmp_path: Path) -> Path:
    p = tmp_path / "src.vault"
    v = Vault(p, PASSWORD)
    v.set("KEY_A", "alpha")
    v.set("KEY_B", "beta")
    v.set("KEY_C", "gamma")
    return p


@pytest.fixture()
def dst_vault(tmp_path: Path) -> Path:
    p = tmp_path / "dst.vault"
    Vault(p, PASSWORD)  # create empty vault
    return p


def test_copy_all_entries(src_vault: Path, dst_vault: Path) -> None:
    count = copy_entries(src_vault, PASSWORD, dst_vault, PASSWORD)
    assert count == 3
    dst = Vault(dst_vault, PASSWORD)
    assert dst.get("KEY_A") == "alpha"
    assert dst.get("KEY_B") == "beta"
    assert dst.get("KEY_C") == "gamma"


def test_copy_selected_keys(src_vault: Path, dst_vault: Path) -> None:
    count = copy_entries(src_vault, PASSWORD, dst_vault, PASSWORD, keys=["KEY_A", "KEY_C"])
    assert count == 2
    dst = Vault(dst_vault, PASSWORD)
    assert dst.get("KEY_A") == "alpha"
    assert dst.get("KEY_B") is None
    assert dst.get("KEY_C") == "gamma"


def test_copy_no_overwrite_skips_existing(src_vault: Path, dst_vault: Path) -> None:
    dst = Vault(dst_vault, PASSWORD)
    dst.set("KEY_A", "original")

    count = copy_entries(src_vault, PASSWORD, dst_vault, PASSWORD, overwrite=False)
    assert count == 2  # KEY_B and KEY_C only
    assert Vault(dst_vault, PASSWORD).get("KEY_A") == "original"


def test_copy_overwrite_replaces_existing(src_vault: Path, dst_vault: Path) -> None:
    dst = Vault(dst_vault, PASSWORD)
    dst.set("KEY_A", "original")

    count = copy_entries(src_vault, PASSWORD, dst_vault, PASSWORD, overwrite=True)
    assert count == 3
    assert Vault(dst_vault, PASSWORD).get("KEY_A") == "alpha"


def test_copy_missing_key_raises(src_vault: Path, dst_vault: Path) -> None:
    with pytest.raises(CopyError, match="KEY_MISSING"):
        copy_entries(src_vault, PASSWORD, dst_vault, PASSWORD, keys=["KEY_MISSING"])


def test_copy_src_not_found(tmp_path: Path, dst_vault: Path) -> None:
    missing = tmp_path / "ghost.vault"
    with pytest.raises(VaultNotFoundError):
        copy_entries(missing, PASSWORD, dst_vault, PASSWORD)


def test_move_removes_from_src(src_vault: Path, dst_vault: Path) -> None:
    count = move_entries(src_vault, PASSWORD, dst_vault, PASSWORD)
    assert count == 3
    src = Vault(src_vault, PASSWORD)
    assert src.keys() == []


def test_move_no_overwrite_does_not_remove_skipped(src_vault: Path, dst_vault: Path) -> None:
    dst = Vault(dst_vault, PASSWORD)
    dst.set("KEY_A", "original")

    move_entries(src_vault, PASSWORD, dst_vault, PASSWORD, overwrite=False)
    # KEY_A was skipped in dst, so it should still exist in src
    src = Vault(src_vault, PASSWORD)
    assert src.get("KEY_A") == "alpha"
    assert src.get("KEY_B") is None
    assert src.get("KEY_C") is None
