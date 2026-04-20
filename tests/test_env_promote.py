"""Tests for envault.env_promote."""
from __future__ import annotations

import pytest
from pathlib import Path

from envault.vault import Vault, VaultNotFoundError
from envault.env_promote import PromoteError, promote_entries


PASSWORD = "test-secret"


@pytest.fixture()
def src_vault(tmp_path: Path) -> Vault:
    v = Vault(tmp_path / "src.vault", PASSWORD)
    v.set("API_KEY", "abc123")
    v.set("DB_URL", "postgres://localhost/dev")
    v.set("DEBUG", "true")
    return v


@pytest.fixture()
def dst_vault(tmp_path: Path) -> Vault:
    v = Vault(tmp_path / "dst.vault", PASSWORD)
    v.set("DB_URL", "postgres://prod-host/prod")
    return v


def test_promote_all_keys(src_vault: Vault, dst_vault: Vault) -> None:
    result = promote_entries(
        src_vault.path, dst_vault.path, PASSWORD, PASSWORD, overwrite=True
    )
    assert result["API_KEY"] == "promoted"
    assert result["DB_URL"] == "promoted"
    assert result["DEBUG"] == "promoted"
    assert Vault(dst_vault.path, PASSWORD).get("API_KEY") == "abc123"


def test_promote_selected_keys(src_vault: Vault, dst_vault: Vault) -> None:
    result = promote_entries(
        src_vault.path, dst_vault.path, PASSWORD, PASSWORD, keys=["API_KEY"], overwrite=True
    )
    assert result == {"API_KEY": "promoted"}


def test_no_overwrite_skips_existing(src_vault: Vault, dst_vault: Vault) -> None:
    result = promote_entries(
        src_vault.path, dst_vault.path, PASSWORD, PASSWORD, overwrite=False
    )
    assert result["DB_URL"] == "skipped"
    # Original destination value must be preserved
    assert Vault(dst_vault.path, PASSWORD).get("DB_URL") == "postgres://prod-host/prod"


def test_overwrite_replaces_existing(src_vault: Vault, dst_vault: Vault) -> None:
    promote_entries(
        src_vault.path, dst_vault.path, PASSWORD, PASSWORD, overwrite=True
    )
    assert Vault(dst_vault.path, PASSWORD).get("DB_URL") == "postgres://localhost/dev"


def test_missing_src_raises(tmp_path: Path, dst_vault: Vault) -> None:
    with pytest.raises(VaultNotFoundError):
        promote_entries(tmp_path / "nope.vault", dst_vault.path, PASSWORD, PASSWORD)


def test_missing_dst_raises(src_vault: Vault, tmp_path: Path) -> None:
    with pytest.raises(VaultNotFoundError):
        promote_entries(src_vault.path, tmp_path / "nope.vault", PASSWORD, PASSWORD)


def test_unknown_key_raises(src_vault: Vault, dst_vault: Vault) -> None:
    with pytest.raises(PromoteError, match="not found in source"):
        promote_entries(
            src_vault.path, dst_vault.path, PASSWORD, PASSWORD, keys=["GHOST_KEY"]
        )


def test_empty_source_returns_empty(tmp_path: Path) -> None:
    src = Vault(tmp_path / "empty.vault", PASSWORD)
    dst = Vault(tmp_path / "dst.vault", PASSWORD)
    result = promote_entries(src.path, dst.path, PASSWORD, PASSWORD)
    assert result == {}
