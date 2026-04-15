"""Tests for envault.cascade."""
from __future__ import annotations

import pytest

from envault.vault import Vault
from envault.cascade import CascadeError, resolve, resolve_with_origins


PASSWORD = "test-password"


@pytest.fixture()
def vault_a(tmp_path):
    path = str(tmp_path / "a.vault")
    v = Vault(path, PASSWORD)
    v.set("SHARED", "from_a")
    v.set("ONLY_A", "alpha")
    return path


@pytest.fixture()
def vault_b(tmp_path):
    path = str(tmp_path / "b.vault")
    v = Vault(path, PASSWORD)
    v.set("SHARED", "from_b")
    v.set("ONLY_B", "beta")
    return path


@pytest.fixture()
def vault_c(tmp_path):
    path = str(tmp_path / "c.vault")
    v = Vault(path, PASSWORD)
    v.set("SHARED", "from_c")
    v.set("ONLY_C", "gamma")
    return path


def test_resolve_single_vault(vault_a):
    result = resolve([vault_a], PASSWORD)
    assert result["ONLY_A"] == "alpha"
    assert result["SHARED"] == "from_a"


def test_resolve_later_vault_wins(vault_a, vault_b):
    result = resolve([vault_a, vault_b], PASSWORD)
    assert result["SHARED"] == "from_b"


def test_resolve_all_keys_present(vault_a, vault_b):
    result = resolve([vault_a, vault_b], PASSWORD)
    assert "ONLY_A" in result
    assert "ONLY_B" in result


def test_resolve_three_vaults_rightmost_wins(vault_a, vault_b, vault_c):
    result = resolve([vault_a, vault_b, vault_c], PASSWORD)
    assert result["SHARED"] == "from_c"


def test_resolve_key_filter(vault_a, vault_b):
    result = resolve([vault_a, vault_b], PASSWORD, keys=["ONLY_A"])
    assert "ONLY_A" in result
    assert "ONLY_B" not in result
    assert "SHARED" not in result


def test_resolve_empty_paths_raises():
    with pytest.raises(CascadeError, match="At least one vault path"):
        resolve([], PASSWORD)


def test_resolve_missing_vault_raises(tmp_path):
    with pytest.raises(CascadeError, match="Vault not found"):
        resolve([str(tmp_path / "ghost.vault")], PASSWORD)


def test_resolve_wrong_password_raises(vault_a):
    with pytest.raises(CascadeError, match="Cannot decrypt"):
        resolve([vault_a], "wrong-password")


def test_resolve_with_origins_tracks_source(vault_a, vault_b):
    result = resolve_with_origins([vault_a, vault_b], PASSWORD)
    value, source = result["SHARED"]
    assert value == "from_b"
    assert source == vault_b


def test_resolve_with_origins_unique_keys_correct_source(vault_a, vault_b):
    result = resolve_with_origins([vault_a, vault_b], PASSWORD)
    assert result["ONLY_A"][1] == vault_a
    assert result["ONLY_B"][1] == vault_b


def test_resolve_with_origins_empty_raises():
    with pytest.raises(CascadeError):
        resolve_with_origins([], PASSWORD)
