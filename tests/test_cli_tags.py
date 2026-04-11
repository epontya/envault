"""CLI integration tests for the 'tag' command group."""

from __future__ import annotations

import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.cli_tags import tag_group
from envault.vault import Vault


PASSWORD = "cli-tag-pass"


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path: Path) -> str:
    path = str(tmp_path / "test.vault")
    v = Vault(path, PASSWORD)
    v.set("DB_URL", "postgres://localhost/db")
    v.set("API_KEY", "abc123")
    return path


def _invoke(runner: CliRunner, vault_file: str, *args: str):
    return runner.invoke(
        tag_group,
        ["--vault", vault_file, *args],
        catch_exceptions=False,
    )


def test_add_tag(runner: CliRunner, vault_file: str) -> None:
    result = _invoke(runner, vault_file, "add", "DB_URL", "database")
    assert result.exit_code == 0
    assert "Tagged 'DB_URL' with 'database'" in result.output


def test_add_tag_missing_key_exits_nonzero(runner: CliRunner, vault_file: str) -> None:
    result = runner.invoke(
        tag_group, ["--vault", vault_file, "add", "GHOST", "x"]
    )
    assert result.exit_code != 0


def test_list_tags(runner: CliRunner, vault_file: str) -> None:
    _invoke(runner, vault_file, "add", "DB_URL", "prod")
    result = _invoke(runner, vault_file, "list", "DB_URL")
    assert "prod" in result.output


def test_list_no_tags(runner: CliRunner, vault_file: str) -> None:
    result = _invoke(runner, vault_file, "list", "API_KEY")
    assert "No tags" in result.output


def test_remove_tag(runner: CliRunner, vault_file: str) -> None:
    _invoke(runner, vault_file, "add", "API_KEY", "secret")
    result = _invoke(runner, vault_file, "remove", "API_KEY", "secret")
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_remove_missing_tag_exits_nonzero(runner: CliRunner, vault_file: str) -> None:
    result = runner.invoke(
        tag_group, ["--vault", vault_file, "remove", "DB_URL", "ghost"]
    )
    assert result.exit_code != 0


def test_find_keys_by_tag(runner: CliRunner, vault_file: str) -> None:
    _invoke(runner, vault_file, "add", "DB_URL", "prod")
    _invoke(runner, vault_file, "add", "API_KEY", "prod")
    result = _invoke(runner, vault_file, "find", "prod")
    assert "DB_URL" in result.output
    assert "API_KEY" in result.output


def test_find_no_match(runner: CliRunner, vault_file: str) -> None:
    result = _invoke(runner, vault_file, "find", "nonexistent")
    assert "No keys found" in result.output


def test_all_tags(runner: CliRunner, vault_file: str) -> None:
    _invoke(runner, vault_file, "add", "DB_URL", "prod")
    _invoke(runner, vault_file, "add", "API_KEY", "secret")
    result = _invoke(runner, vault_file, "all")
    assert "prod" in result.output
    assert "secret" in result.output
