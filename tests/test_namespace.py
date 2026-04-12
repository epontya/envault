"""Tests for envault.namespace and envault.cli_namespace."""

from __future__ import annotations

import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.namespace import NamespaceError, NamespaceStore
from envault.cli_namespace import namespace_group


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def store(tmp_path: Path) -> NamespaceStore:
    return NamespaceStore(tmp_path / "ns.json")


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def vault_file(tmp_path: Path) -> str:
    return str(tmp_path / "vault.db")


def _invoke(runner: CliRunner, vault_file: str, *args: str):
    return runner.invoke(namespace_group, [*args, "--vault", vault_file])


# ---------------------------------------------------------------------------
# Unit tests — NamespaceStore
# ---------------------------------------------------------------------------

def test_assign_and_get(store: NamespaceStore) -> None:
    store.assign("DB_HOST", "database")
    assert store.get_namespace("DB_HOST") == "database"


def test_get_missing_returns_none(store: NamespaceStore) -> None:
    assert store.get_namespace("MISSING") is None


def test_keys_in_namespace_sorted(store: NamespaceStore) -> None:
    store.assign("Z_KEY", "app")
    store.assign("A_KEY", "app")
    store.assign("OTHER", "infra")
    assert store.keys_in("app") == ["A_KEY", "Z_KEY"]


def test_list_namespaces_sorted(store: NamespaceStore) -> None:
    store.assign("K1", "beta")
    store.assign("K2", "alpha")
    assert store.list_namespaces() == ["alpha", "beta"]


def test_unassign_existing(store: NamespaceStore) -> None:
    store.assign("KEY", "ns")
    assert store.unassign("KEY") is True
    assert store.get_namespace("KEY") is None


def test_unassign_missing_returns_false(store: NamespaceStore) -> None:
    assert store.unassign("GHOST") is False


def test_rename_updates_all_keys(store: NamespaceStore) -> None:
    store.assign("A", "old")
    store.assign("B", "old")
    store.assign("C", "other")
    count = store.rename("old", "new")
    assert count == 2
    assert store.keys_in("new") == ["A", "B"]
    assert store.keys_in("old") == []


def test_empty_key_raises(store: NamespaceStore) -> None:
    with pytest.raises(NamespaceError):
        store.assign("", "ns")


def test_empty_namespace_raises(store: NamespaceStore) -> None:
    with pytest.raises(NamespaceError):
        store.assign("KEY", "")


def test_persistence(tmp_path: Path) -> None:
    path = tmp_path / "ns.json"
    s1 = NamespaceStore(path)
    s1.assign("FOO", "bar")
    s2 = NamespaceStore(path)
    assert s2.get_namespace("FOO") == "bar"


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

def test_cli_assign_and_get(runner: CliRunner, vault_file: str) -> None:
    result = _invoke(runner, vault_file, "assign", "API_KEY", "secrets")
    assert result.exit_code == 0
    assert "secrets" in result.output

    result = _invoke(runner, vault_file, "get", "API_KEY")
    assert result.exit_code == 0
    assert "secrets" in result.output


def test_cli_get_missing_exits_nonzero(runner: CliRunner, vault_file: str) -> None:
    result = _invoke(runner, vault_file, "get", "MISSING")
    assert result.exit_code != 0


def test_cli_list_keys(runner: CliRunner, vault_file: str) -> None:
    _invoke(runner, vault_file, "assign", "K1", "myns")
    _invoke(runner, vault_file, "assign", "K2", "myns")
    result = _invoke(runner, vault_file, "list", "myns")
    assert "K1" in result.output
    assert "K2" in result.output


def test_cli_namespaces_lists_all(runner: CliRunner, vault_file: str) -> None:
    _invoke(runner, vault_file, "assign", "X", "alpha")
    _invoke(runner, vault_file, "assign", "Y", "beta")
    result = _invoke(runner, vault_file, "namespaces")
    assert "alpha" in result.output
    assert "beta" in result.output


def test_cli_unassign(runner: CliRunner, vault_file: str) -> None:
    _invoke(runner, vault_file, "assign", "Z", "tmp")
    result = _invoke(runner, vault_file, "unassign", "Z")
    assert result.exit_code == 0


def test_cli_rename(runner: CliRunner, vault_file: str) -> None:
    _invoke(runner, vault_file, "assign", "P", "old")
    result = _invoke(runner, vault_file, "rename", "old", "new")
    assert result.exit_code == 0
    assert "1" in result.output
