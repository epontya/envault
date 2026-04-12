"""Tests for envault.cli_quota."""

from __future__ import annotations

import pytest
from pathlib import Path
from click.testing import CliRunner

from envault.cli_quota import quota_group


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path: Path) -> str:
    return str(tmp_path / "test.vault")


def _invoke(runner: CliRunner, vault_file: str, *args: str):
    return runner.invoke(quota_group, [*args, "--vault", vault_file])


def test_get_shows_defaults(runner: CliRunner, vault_file: str) -> None:
    result = _invoke(runner, vault_file, "get")
    assert result.exit_code == 0
    assert "max_entries" in result.output
    assert "500" in result.output


def test_set_max_entries(runner: CliRunner, vault_file: str) -> None:
    result = _invoke(runner, vault_file, "set", "--max-entries", "50")
    assert result.exit_code == 0
    assert "updated" in result.output.lower()


def test_set_then_get_reflects_change(runner: CliRunner, vault_file: str) -> None:
    _invoke(runner, vault_file, "set", "--max-entries", "42")
    result = _invoke(runner, vault_file, "get")
    assert "42" in result.output


def test_set_no_options_fails(runner: CliRunner, vault_file: str) -> None:
    result = _invoke(runner, vault_file, "set")
    assert result.exit_code != 0


def test_set_invalid_value_exits_nonzero(runner: CliRunner, vault_file: str) -> None:
    result = _invoke(runner, vault_file, "set", "--max-entries", "0")
    assert result.exit_code != 0


def test_reset_restores_defaults(runner: CliRunner, vault_file: str) -> None:
    _invoke(runner, vault_file, "set", "--max-entries", "3")
    result = _invoke(runner, vault_file, "reset")
    assert result.exit_code == 0
    get_result = _invoke(runner, vault_file, "get")
    assert "500" in get_result.output


def test_set_multiple_limits(runner: CliRunner, vault_file: str) -> None:
    result = _invoke(
        runner, vault_file,
        "set", "--max-entries", "10",
        "--max-value-bytes", "128",
        "--max-total-bytes", "1024",
    )
    assert result.exit_code == 0
    get_result = _invoke(runner, vault_file, "get")
    assert "10" in get_result.output
    assert "128" in get_result.output
    assert "1024" in get_result.output
