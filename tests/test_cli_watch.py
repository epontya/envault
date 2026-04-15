"""Tests for envault.cli_watch."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_watch import watch_group
from envault.vault import Vault


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def vault_file(tmp_path: Path) -> Path:
    p = tmp_path / "test.vault"
    v = Vault(p, "pass")
    v.set("DB_URL", "postgres://localhost/mydb")
    v.set("API_KEY", "abc123")
    return p


def _invoke(runner: CliRunner, vault_file: Path, *args: str, password: str = "pass"):
    return runner.invoke(
        watch_group,
        list(args),
        input=password + "\n",
        catch_exceptions=False,
    )


def test_add_watch_success(runner: CliRunner, vault_file: Path) -> None:
    result = _invoke(runner, vault_file, "add", str(vault_file), "DB_URL", "slack-notify")
    assert result.exit_code == 0
    assert "DB_URL" in result.output
    assert "slack-notify" in result.output


def test_add_duplicate_exits_nonzero(runner: CliRunner, vault_file: Path) -> None:
    _invoke(runner, vault_file, "add", str(vault_file), "DB_URL", "lbl")
    result = _invoke(runner, vault_file, "add", str(vault_file), "DB_URL", "lbl2")
    assert result.exit_code != 0


def test_list_empty(runner: CliRunner, vault_file: Path) -> None:
    result = runner.invoke(watch_group, ["list", str(vault_file)])
    assert result.exit_code == 0
    assert "No active watches" in result.output


def test_list_shows_added_watches(runner: CliRunner, vault_file: Path) -> None:
    _invoke(runner, vault_file, "add", str(vault_file), "API_KEY", "log")
    result = runner.invoke(watch_group, ["list", str(vault_file)])
    assert "API_KEY" in result.output
    assert "log" in result.output


def test_remove_existing(runner: CliRunner, vault_file: Path) -> None:
    _invoke(runner, vault_file, "add", str(vault_file), "API_KEY", "lbl")
    result = runner.invoke(watch_group, ["remove", str(vault_file), "API_KEY"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_missing_exits_nonzero(runner: CliRunner, vault_file: Path) -> None:
    result = runner.invoke(watch_group, ["remove", str(vault_file), "GHOST"])
    assert result.exit_code != 0


def test_check_detects_no_change(runner: CliRunner, vault_file: Path) -> None:
    _invoke(runner, vault_file, "add", str(vault_file), "DB_URL", "lbl")
    result = _invoke(runner, vault_file, "check", str(vault_file))
    assert result.exit_code == 0
    assert "No changes" in result.output
