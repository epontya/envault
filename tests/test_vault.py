"""Tests for the Vault class."""

import pytest
from pathlib import Path

from envault.vault import Vault, VaultNotFoundError

PASSWORD = "test-password-123"


@pytest.fixture
def tmp_vault(tmp_path):
    """Return a Vault instance backed by a temporary directory."""
    return Vault("test", vault_dir=tmp_path)


def test_set_and_get(tmp_vault):
    tmp_vault.set("KEY", "value")
    assert tmp_vault.get("KEY") == "value"


def test_get_missing_key_returns_none(tmp_vault):
    assert tmp_vault.get("MISSING") is None


def test_delete_existing_key(tmp_vault):
    tmp_vault.set("KEY", "value")
    result = tmp_vault.delete("KEY")
    assert result is True
    assert tmp_vault.get("KEY") is None


def test_delete_missing_key_returns_false(tmp_vault):
    assert tmp_vault.delete("NOPE") is False


def test_list_keys(tmp_vault):
    tmp_vault.set("A", "1")
    tmp_vault.set("B", "2")
    assert sorted(tmp_vault.list_keys()) == ["A", "B"]


def test_save_creates_file(tmp_path):
    vault = Vault("myproject", vault_dir=tmp_path)
    vault.set("DB_URL", "postgres://localhost/db")
    vault.save(PASSWORD)
    assert (tmp_path / "myproject.vault").exists()


def test_round_trip_save_load(tmp_path):
    vault = Vault("myproject", vault_dir=tmp_path)
    vault.set("SECRET", "supersecret")
    vault.set("API_KEY", "abc123")
    vault.save(PASSWORD)

    loaded = Vault("myproject", vault_dir=tmp_path)
    loaded.load(PASSWORD)
    assert loaded.get("SECRET") == "supersecret"
    assert loaded.get("API_KEY") == "abc123"


def test_load_wrong_password_raises(tmp_path):
    vault = Vault("myproject", vault_dir=tmp_path)
    vault.set("KEY", "val")
    vault.save(PASSWORD)

    other = Vault("myproject", vault_dir=tmp_path)
    with pytest.raises(ValueError):
        other.load("wrong-password")


def test_load_nonexistent_vault_raises(tmp_path):
    vault = Vault("ghost", vault_dir=tmp_path)
    with pytest.raises(VaultNotFoundError):
        vault.load(PASSWORD)


def test_exists_true(tmp_path):
    vault = Vault("exists", vault_dir=tmp_path)
    vault.save(PASSWORD)
    assert Vault.exists("exists", vault_dir=tmp_path) is True


def test_exists_false(tmp_path):
    assert Vault.exists("nope", vault_dir=tmp_path) is False
