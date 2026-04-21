"""Tests for envault.env_chain."""
from __future__ import annotations

import pytest
from pathlib import Path

from envault.vault import Vault
from envault.env_chain import (
    ChainError,
    add_vault,
    list_chain,
    remove_vault,
    resolve_key,
    resolve_all,
    _chain_path,
)

PASSWORD = "test-password"


@pytest.fixture()
def primary(tmp_path: Path) -> Path:
    vp = tmp_path / "primary.vault"
    v = Vault(vp, PASSWORD)
    v.set("KEY_A", "alpha")
    v.set("SHARED", "from-primary")
    return vp


@pytest.fixture()
def secondary(tmp_path: Path) -> Path:
    vp = tmp_path / "secondary.vault"
    v = Vault(vp, PASSWORD)
    v.set("KEY_B", "beta")
    v.set("SHARED", "from-secondary")
    return vp


@pytest.fixture()
def tertiary(tmp_path: Path) -> Path:
    vp = tmp_path / "tertiary.vault"
    v = Vault(vp, PASSWORD)
    v.set("KEY_C", "gamma")
    return vp


def test_add_vault_creates_chain_file(primary, secondary):
    add_vault(primary, secondary)
    assert _chain_path(primary).exists()


def test_add_vault_returns_chain(primary, secondary):
    chain = add_vault(primary, secondary)
    assert str(secondary) in chain


def test_add_duplicate_raises(primary, secondary):
    add_vault(primary, secondary)
    with pytest.raises(ChainError):
        add_vault(primary, secondary)


def test_list_chain_empty(primary):
    assert list_chain(primary) == []


def test_list_chain_after_add(primary, secondary, tertiary):
    add_vault(primary, secondary)
    add_vault(primary, tertiary)
    chain = list_chain(primary)
    assert len(chain) == 2
    assert str(secondary) == chain[0]
    assert str(tertiary) == chain[1]


def test_remove_existing_returns_true(primary, secondary):
    add_vault(primary, secondary)
    assert remove_vault(primary, secondary) is True
    assert list_chain(primary) == []


def test_remove_missing_returns_false(primary, secondary):
    assert remove_vault(primary, secondary) is False


def test_resolve_key_found_in_primary(primary, secondary):
    add_vault(primary, secondary)
    assert resolve_key(primary, "KEY_A", PASSWORD) == "alpha"


def test_resolve_key_found_in_secondary(primary, secondary):
    add_vault(primary, secondary)
    assert resolve_key(primary, "KEY_B", PASSWORD) == "beta"


def test_resolve_key_primary_wins_on_conflict(primary, secondary):
    add_vault(primary, secondary)
    assert resolve_key(primary, "SHARED", PASSWORD) == "from-primary"


def test_resolve_key_missing_returns_none(primary, secondary):
    add_vault(primary, secondary)
    assert resolve_key(primary, "DOES_NOT_EXIST", PASSWORD) is None


def test_resolve_all_merges_keys(primary, secondary):
    add_vault(primary, secondary)
    merged = resolve_all(primary, PASSWORD)
    assert "KEY_A" in merged
    assert "KEY_B" in merged


def test_resolve_all_primary_wins(primary, secondary):
    add_vault(primary, secondary)
    merged = resolve_all(primary, PASSWORD)
    assert merged["SHARED"] == "from-primary"


def test_resolve_all_empty_chain(primary):
    merged = resolve_all(primary, PASSWORD)
    assert merged == {"KEY_A": "alpha", "SHARED": "from-primary"}
