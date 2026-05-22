"""Tests for envault.cli_pin_policy CLI commands."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_pin_policy import pin_policy_group
from envault.env_pin_policy import get_policy, _policy_path


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def vault_file(tmp_path: Path) -> Path:
    p = tmp_path / "my.vault"
    p.write_text("{}")
    return p


def _invoke(runner: CliRunner, *args):
    return runner.invoke(pin_policy_group, [str(a) for a in args])


def test_set_success(runner: CliRunner, vault_file: Path) -> None:
    result = _invoke(runner, "set", vault_file, "--require", "--min-length", "6")
    assert result.exit_code == 0
    assert "require_pin=True" in result.output
    assert "min_pin_length=6" in result.output


def test_set_invalid_min_length_exits_nonzero(
    runner: CliRunner, vault_file: Path
) -> None:
    result = _invoke(runner, "set", vault_file, "--min-length", "2")
    assert result.exit_code != 0
    assert "min_pin_length" in result.output


def test_show_defaults(runner: CliRunner, vault_file: Path) -> None:
    result = _invoke(runner, "show", vault_file)
    assert result.exit_code == 0
    assert "require_pin" in result.output
    assert "False" in result.output


def test_show_reflects_set_values(runner: CliRunner, vault_file: Path) -> None:
    _invoke(runner, "set", vault_file, "--require", "--min-length", "8")
    result = _invoke(runner, "show", vault_file)
    assert "True" in result.output
    assert "8" in result.output


def test_remove_existing_policy(runner: CliRunner, vault_file: Path) -> None:
    _invoke(runner, "set", vault_file)
    result = _invoke(runner, "remove", vault_file)
    assert result.exit_code == 0
    assert "removed" in result.output
    assert not _policy_path(vault_file).exists()


def test_remove_nonexistent_policy(runner: CliRunner, vault_file: Path) -> None:
    result = _invoke(runner, "remove", vault_file)
    assert result.exit_code == 0
    assert "No PIN policy" in result.output


def test_check_valid_pin(runner: CliRunner, vault_file: Path) -> None:
    _invoke(runner, "set", vault_file, "--require", "--min-length", "4")
    result = _invoke(runner, "check", vault_file, "1234")
    assert result.exit_code == 0
    assert "satisfies" in result.output


def test_check_invalid_pin_exits_nonzero(runner: CliRunner, vault_file: Path) -> None:
    _invoke(runner, "set", vault_file, "--require", "--min-length", "6")
    result = _invoke(runner, "check", vault_file, "123")
    assert result.exit_code != 0
