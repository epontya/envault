"""Tests for envault.alias and envault.cli_alias."""

from __future__ import annotations

import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.alias import AliasError, AliasStore
from envault.cli_alias import alias_group
from envault.vault import Vault


# ---------------------------------------------------------------------------
# Unit tests – AliasStore
# ---------------------------------------------------------------------------

@pytest.fixture()
def store(tmp_path: Path) -> AliasStore:
    return AliasStore(tmp_path / "aliases.json")


def test_add_and_resolve(store: AliasStore) -> None:
    store.add("db", "DATABASE_URL")
    assert store.resolve("db") == "DATABASE_URL"


def test_resolve_missing_returns_none(store: AliasStore) -> None:
    assert store.resolve("nope") is None


def test_exists(store: AliasStore) -> None:
    store.add("db", "DATABASE_URL")
    assert store.exists("db") is True
    assert store.exists("other") is False


def test_duplicate_alias_raises(store: AliasStore) -> None:
    store.add("db", "DATABASE_URL")
    with pytest.raises(AliasError, match="already exists"):
        store.add("db", "ANOTHER_URL")


def test_invalid_alias_name_raises(store: AliasStore) -> None:
    with pytest.raises(AliasError, match="Invalid alias"):
        store.add("bad-name!", "KEY")


def test_empty_key_raises(store: AliasStore) -> None:
    with pytest.raises(AliasError, match="empty"):
        store.add("myalias", "")


def test_remove_existing(store: AliasStore) -> None:
    store.add("db", "DATABASE_URL")
    assert store.remove("db") is True
    assert store.resolve("db") is None


def test_remove_missing_returns_false(store: AliasStore) -> None:
    assert store.remove("ghost") is False


def test_list_aliases_sorted(store: AliasStore) -> None:
    store.add("z_key", "Z")
    store.add("a_key", "A")
    pairs = store.list_aliases()
    assert pairs == [("a_key", "A"), ("z_key", "Z")]


def test_persistence(tmp_path: Path) -> None:
    s1 = AliasStore(tmp_path / "aliases.json")
    s1.add("db", "DATABASE_URL")
    s2 = AliasStore(tmp_path / "aliases.json")
    assert s2.resolve("db") == "DATABASE_URL"


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def vault_file(tmp_path: Path) -> Path:
    vf = tmp_path / "test.vault"
    v = Vault(vf, "secret")
    v.set("DATABASE_URL", "postgres://localhost/db")
    return vf


def _invoke(runner: CliRunner, vault_file: Path, *args: str):
    return runner.invoke(
        alias_group,
        [*args, "--vault", str(vault_file)],
        catch_exceptions=False,
    )


def test_cli_add_and_list(runner: CliRunner, vault_file: Path) -> None:
    result = _invoke(runner, vault_file, "add", "db", "DATABASE_URL")
    assert result.exit_code == 0
    assert "added" in result.output

    result = _invoke(runner, vault_file, "list")
    assert result.exit_code == 0
    assert "db" in result.output
    assert "DATABASE_URL" in result.output


def test_cli_resolve(runner: CliRunner, vault_file: Path) -> None:
    _invoke(runner, vault_file, "add", "db", "DATABASE_URL")
    result = _invoke(runner, vault_file, "resolve", "db")
    assert result.exit_code == 0
    assert "DATABASE_URL" in result.output


def test_cli_remove(runner: CliRunner, vault_file: Path) -> None:
    _invoke(runner, vault_file, "add", "db", "DATABASE_URL")
    result = _invoke(runner, vault_file, "remove", "db")
    assert result.exit_code == 0
    assert "removed" in result.output


def test_cli_list_empty(runner: CliRunner, vault_file: Path) -> None:
    result = _invoke(runner, vault_file, "list")
    assert result.exit_code == 0
    assert "No aliases" in result.output


def test_cli_resolve_missing_exits_nonzero(runner: CliRunner, vault_file: Path) -> None:
    result = runner.invoke(
        alias_group,
        ["resolve", "ghost", "--vault", str(vault_file)],
    )
    assert result.exit_code != 0
