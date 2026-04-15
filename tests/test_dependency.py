"""Tests for envault.dependency and envault.cli_dependency."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.dependency import DependencyError, DependencyStore
from envault.cli_dependency import dep_group


@pytest.fixture()
def store(tmp_path: Path) -> DependencyStore:
    return DependencyStore(tmp_path / "vault.json")


# --- DependencyStore unit tests ---

def test_add_and_get(store: DependencyStore) -> None:
    store.add("APP_URL", "BASE_URL")
    assert "BASE_URL" in store.get("APP_URL")


def test_add_self_raises(store: DependencyStore) -> None:
    with pytest.raises(DependencyError):
        store.add("KEY", "KEY")


def test_duplicate_add_ignored(store: DependencyStore) -> None:
    store.add("A", "B")
    store.add("A", "B")
    assert store.get("A").count("B") == 1


def test_remove_existing(store: DependencyStore) -> None:
    store.add("A", "B")
    assert store.remove("A", "B") is True
    assert store.get("A") == []


def test_remove_missing_returns_false(store: DependencyStore) -> None:
    assert store.remove("X", "Y") is False


def test_dependents(store: DependencyStore) -> None:
    store.add("A", "BASE")
    store.add("B", "BASE")
    result = store.dependents("BASE")
    assert sorted(result) == ["A", "B"]


def test_all_dependencies_transitive(store: DependencyStore) -> None:
    store.add("C", "B")
    store.add("B", "A")
    result = store.all_dependencies("C")
    assert result == {"A", "B"}


def test_remove_key_cleans_up(store: DependencyStore) -> None:
    store.add("A", "B")
    store.add("C", "A")
    store.remove_key("A")
    assert store.get("A") == []
    assert "A" not in store.dependents("B")


# --- CLI tests ---

@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def vault_file(tmp_path: Path) -> str:
    return str(tmp_path / "vault.json")


def _invoke(runner: CliRunner, vault_file: str, *args: str):
    return runner.invoke(dep_group, ["--vault", vault_file, *args])


def test_cli_add_success(runner: CliRunner, vault_file: str) -> None:
    result = _invoke(runner, vault_file, "add", "APP", "BASE")
    assert result.exit_code == 0
    assert "APP -> BASE" in result.output


def test_cli_add_self_exits_nonzero(runner: CliRunner, vault_file: str) -> None:
    result = _invoke(runner, vault_file, "add", "KEY", "KEY")
    assert result.exit_code != 0


def test_cli_list_shows_deps(runner: CliRunner, vault_file: str) -> None:
    _invoke(runner, vault_file, "add", "APP", "BASE")
    result = _invoke(runner, vault_file, "list", "APP")
    assert "BASE" in result.output


def test_cli_remove_success(runner: CliRunner, vault_file: str) -> None:
    _invoke(runner, vault_file, "add", "APP", "BASE")
    result = _invoke(runner, vault_file, "remove", "APP", "BASE")
    assert result.exit_code == 0


def test_cli_remove_missing_exits_nonzero(runner: CliRunner, vault_file: str) -> None:
    result = _invoke(runner, vault_file, "remove", "X", "Y")
    assert result.exit_code != 0


def test_cli_dependents(runner: CliRunner, vault_file: str) -> None:
    _invoke(runner, vault_file, "add", "A", "ROOT")
    _invoke(runner, vault_file, "add", "B", "ROOT")
    result = _invoke(runner, vault_file, "dependents", "ROOT")
    assert "A" in result.output
    assert "B" in result.output
