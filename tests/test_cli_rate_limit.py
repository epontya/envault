"""Tests for envault.cli_rate_limit."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_rate_limit import rate_limit_group


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path: Path) -> str:
    vf = tmp_path / "test.vault"
    vf.write_text("{}")
    return str(vf)


def _invoke(runner: CliRunner, vault_file: str, *args: str):
    return runner.invoke(rate_limit_group, [*args, "--vault", vault_file])


def test_set_creates_limit(runner: CliRunner, vault_file: str) -> None:
    result = _invoke(runner, vault_file, "set", "get", "--max-calls", "5", "--window", "60")
    assert result.exit_code == 0
    assert "get" in result.output
    assert "5" in result.output


def test_set_invalid_max_calls_exits_nonzero(runner: CliRunner, vault_file: str) -> None:
    result = _invoke(runner, vault_file, "set", "get", "--max-calls", "0", "--window", "60")
    assert result.exit_code != 0
    assert "Error" in result.output


def test_get_shows_config(runner: CliRunner, vault_file: str) -> None:
    _invoke(runner, vault_file, "set", "delete", "--max-calls", "3", "--window", "30")
    result = _invoke(runner, vault_file, "get", "delete")
    assert result.exit_code == 0
    assert "max_calls" in result.output
    assert "3" in result.output


def test_get_missing_exits_nonzero(runner: CliRunner, vault_file: str) -> None:
    result = _invoke(runner, vault_file, "get", "nonexistent")
    assert result.exit_code != 0


def test_remove_existing(runner: CliRunner, vault_file: str) -> None:
    _invoke(runner, vault_file, "set", "rotate", "--max-calls", "2", "--window", "10")
    result = _invoke(runner, vault_file, "remove", "rotate")
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_missing_exits_nonzero(runner: CliRunner, vault_file: str) -> None:
    result = _invoke(runner, vault_file, "remove", "ghost")
    assert result.exit_code != 0


def test_list_empty(runner: CliRunner, vault_file: str) -> None:
    result = _invoke(runner, vault_file, "list")
    assert result.exit_code == 0
    assert "No rate limits" in result.output


def test_list_shows_all(runner: CliRunner, vault_file: str) -> None:
    _invoke(runner, vault_file, "set", "set", "--max-calls", "5", "--window", "60")
    _invoke(runner, vault_file, "set", "get", "--max-calls", "10", "--window", "60")
    result = _invoke(runner, vault_file, "list")
    assert result.exit_code == 0
    assert "set" in result.output
    assert "get" in result.output
