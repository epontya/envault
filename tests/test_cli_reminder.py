"""Tests for envault.cli_reminder."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli import cli
from envault.cli_reminder import reminder_group
from envault.vault import Vault


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def vault_file(tmp_path: Path) -> Path:
    vp = tmp_path / ".envault"
    v = Vault(vp, "secret")
    v.set("API_KEY", "abc123")
    return vp


def _invoke(runner, vault_file, *args):
    return runner.invoke(
        reminder_group,
        list(args) + ["--vault", str(vault_file)],
        catch_exceptions=False,
    )


def _future_iso(days: int = 1) -> str:
    dt = datetime.now(timezone.utc) + timedelta(days=days)
    return dt.isoformat()


def _past_iso(days: int = 1) -> str:
    dt = datetime.now(timezone.utc) - timedelta(days=days)
    return dt.isoformat()


def test_set_reminder_success(runner, vault_file):
    result = runner.invoke(
        reminder_group,
        ["set", "API_KEY", _future_iso(), "--vault", str(vault_file), "--password", "secret"],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "Reminder set" in result.output


def test_set_reminder_missing_key_exits_nonzero(runner, vault_file):
    result = runner.invoke(
        reminder_group,
        ["set", "GHOST", _future_iso(), "--vault", str(vault_file), "--password", "secret"],
        catch_exceptions=False,
    )
    assert result.exit_code != 0


def test_set_reminder_bad_datetime_exits_nonzero(runner, vault_file):
    result = runner.invoke(
        reminder_group,
        ["set", "API_KEY", "not-a-date", "--vault", str(vault_file), "--password", "secret"],
        catch_exceptions=False,
    )
    assert result.exit_code != 0


def test_list_shows_reminder(runner, vault_file):
    runner.invoke(
        reminder_group,
        ["set", "API_KEY", _future_iso(), "--note", "check me", "--vault", str(vault_file), "--password", "secret"],
        catch_exceptions=False,
    )
    result = _invoke(runner, vault_file, "list")
    assert "API_KEY" in result.output


def test_list_due_only(runner, vault_file):
    # set one past, one future
    runner.invoke(
        reminder_group,
        ["set", "API_KEY", _past_iso(), "--vault", str(vault_file), "--password", "secret"],
        catch_exceptions=False,
    )
    result = _invoke(runner, vault_file, "list", "--due")
    assert "API_KEY" in result.output


def test_remove_reminder(runner, vault_file):
    runner.invoke(
        reminder_group,
        ["set", "API_KEY", _future_iso(), "--vault", str(vault_file), "--password", "secret"],
        catch_exceptions=False,
    )
    result = _invoke(runner, vault_file, "remove", "API_KEY")
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_missing_exits_nonzero(runner, vault_file):
    result = _invoke(runner, vault_file, "remove", "GHOST")
    assert result.exit_code != 0
