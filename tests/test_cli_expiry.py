"""Tests for envault.cli_expiry."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_expiry import expiry_group
from envault.vault import Vault

FUTURE = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
PAST = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
PASSWORD = "testpassword"


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def vault_file(tmp_path: Path) -> str:
    vf = str(tmp_path / "test.vault")
    v = Vault(vf, PASSWORD)
    v.set("MY_KEY", "hello")
    v.set("OLD_KEY", "bye")
    return vf


def _invoke(runner: CliRunner, vault_file: str, *args: str):
    return runner.invoke(
        expiry_group,
        [*args, "--vault", vault_file],
        catch_exceptions=False,
    )


def test_set_expiry_success(runner: CliRunner, vault_file: str) -> None:
    result = _invoke(runner, vault_file, "set", "MY_KEY", FUTURE)
    assert result.exit_code == 0
    assert "MY_KEY" in result.output


def test_set_expiry_missing_key_exits_nonzero(runner: CliRunner, vault_file: str) -> None:
    result = runner.invoke(
        expiry_group,
        ["set", "NO_SUCH_KEY", FUTURE, "--vault", vault_file],
        catch_exceptions=False,
    )
    assert result.exit_code != 0


def test_get_expiry_shows_status(runner: CliRunner, vault_file: str) -> None:
    _invoke(runner, vault_file, "set", "MY_KEY", FUTURE)
    result = _invoke(runner, vault_file, "get", "MY_KEY")
    assert result.exit_code == 0
    assert "active" in result.output


def test_get_expiry_shows_expired(runner: CliRunner, vault_file: str) -> None:
    _invoke(runner, vault_file, "set", "OLD_KEY", PAST)
    result = _invoke(runner, vault_file, "get", "OLD_KEY")
    assert result.exit_code == 0
    assert "EXPIRED" in result.output


def test_get_expiry_no_expiry_set(runner: CliRunner, vault_file: str) -> None:
    result = _invoke(runner, vault_file, "get", "MY_KEY")
    assert result.exit_code == 0
    assert "No expiry" in result.output


def test_remove_expiry(runner: CliRunner, vault_file: str) -> None:
    _invoke(runner, vault_file, "set", "MY_KEY", FUTURE)
    result = _invoke(runner, vault_file, "remove", "MY_KEY")
    assert result.exit_code == 0
    assert "removed" in result.output


def test_list_shows_all(runner: CliRunner, vault_file: str) -> None:
    _invoke(runner, vault_file, "set", "MY_KEY", FUTURE)
    _invoke(runner, vault_file, "set", "OLD_KEY", PAST)
    result = _invoke(runner, vault_file, "list")
    assert result.exit_code == 0
    assert "MY_KEY" in result.output
    assert "OLD_KEY" in result.output


def test_list_expired_only(runner: CliRunner, vault_file: str) -> None:
    _invoke(runner, vault_file, "set", "MY_KEY", FUTURE)
    _invoke(runner, vault_file, "set", "OLD_KEY", PAST)
    result = _invoke(runner, vault_file, "list", "--expired-only")
    assert result.exit_code == 0
    assert "OLD_KEY" in result.output
    assert "MY_KEY" not in result.output
