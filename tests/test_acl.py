"""Tests for envault.acl."""
from __future__ import annotations

import pytest
from pathlib import Path

from envault.acl import ACLError, ACLStore


@pytest.fixture
def store(tmp_path: Path) -> ACLStore:
    return ACLStore(tmp_path / ".envault_acl.json")


def test_grant_creates_file(store: ACLStore, tmp_path: Path) -> None:
    store.grant("DB_URL", "admin", "read")
    assert (tmp_path / ".envault_acl.json").exists()


def test_grant_and_can(store: ACLStore) -> None:
    store.grant("DB_URL", "admin", "read")
    assert store.can("DB_URL", "admin", "read") is True


def test_can_returns_false_when_not_granted(store: ACLStore) -> None:
    assert store.can("DB_URL", "admin", "write") is False


def test_duplicate_grant_not_duplicated(store: ACLStore) -> None:
    store.grant("KEY", "dev", "read")
    store.grant("KEY", "dev", "read")
    assert store.permissions("KEY", "dev").count("read") == 1


def test_grant_invalid_permission_raises(store: ACLStore) -> None:
    with pytest.raises(ACLError, match="Invalid permission"):
        store.grant("KEY", "dev", "execute")


def test_revoke_existing(store: ACLStore) -> None:
    store.grant("API_KEY", "ci", "read")
    result = store.revoke("API_KEY", "ci", "read")
    assert result is True
    assert store.can("API_KEY", "ci", "read") is False


def test_revoke_missing_returns_false(store: ACLStore) -> None:
    assert store.revoke("MISSING", "nobody", "write") is False


def test_revoke_cleans_up_empty_role(store: ACLStore) -> None:
    store.grant("X", "role", "read")
    store.revoke("X", "role", "read")
    assert store.roles_for_key("X") == {}


def test_permissions_returns_list(store: ACLStore) -> None:
    store.grant("SECRET", "ops", "read")
    store.grant("SECRET", "ops", "write")
    perms = store.permissions("SECRET", "ops")
    assert set(perms) == {"read", "write"}


def test_roles_for_key(store: ACLStore) -> None:
    store.grant("TOKEN", "admin", "read")
    store.grant("TOKEN", "admin", "write")
    store.grant("TOKEN", "viewer", "read")
    roles = store.roles_for_key("TOKEN")
    assert "admin" in roles
    assert "viewer" in roles


def test_remove_key(store: ACLStore) -> None:
    store.grant("GONE", "admin", "read")
    result = store.remove_key("GONE")
    assert result is True
    assert store.roles_for_key("GONE") == {}


def test_remove_missing_key_returns_false(store: ACLStore) -> None:
    assert store.remove_key("NEVER_EXISTED") is False


def test_persistence(tmp_path: Path) -> None:
    acl_path = tmp_path / ".envault_acl.json"
    s1 = ACLStore(acl_path)
    s1.grant("DB", "admin", "write")
    s2 = ACLStore(acl_path)
    assert s2.can("DB", "admin", "write") is True
