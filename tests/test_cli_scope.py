"""Tests for envault/cli_scope.py"""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_scope import scope_group
from envault.env_scope import assign_scope


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_file(tmp_path):
    return str(tmp_path / "vault.db")


def _invoke(runner, vault_file, *args):
    return runner.invoke(
        scope_group,
        list(args),
        obj={"vault_path": vault_file},
        catch_exceptions=False,
    )


def test_assign_success(runner, vault_file):
    result = _invoke(runner, vault_file, "assign", "DB_URL", "dev")
    assert result.exit_code == 0
    assert "dev" in result.output


def test_assign_empty_key_exits_nonzero(runner, vault_file):
    result = runner.invoke(
        scope_group,
        ["assign", "", "dev"],
        obj={"vault_path": vault_file},
    )
    assert result.exit_code != 0


def test_remove_existing_scope(runner, vault_file):
    assign_scope(vault_file, "TOKEN", "prod")
    result = _invoke(runner, vault_file, "remove", "TOKEN", "prod")
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_remove_nonexistent_scope(runner, vault_file):
    result = _invoke(runner, vault_file, "remove", "TOKEN", "dev")
    assert result.exit_code == 0
    assert "not in scope" in result.output


def test_get_shows_scopes(runner, vault_file):
    assign_scope(vault_file, "API_KEY", "staging")
    result = _invoke(runner, vault_file, "get", "API_KEY")
    assert result.exit_code == 0
    assert "staging" in result.output


def test_get_missing_key_shows_message(runner, vault_file):
    result = _invoke(runner, vault_file, "get", "MISSING")
    assert result.exit_code == 0
    assert "No scopes" in result.output


def test_keys_in_scope(runner, vault_file):
    assign_scope(vault_file, "DB_URL", "dev")
    result = _invoke(runner, vault_file, "keys", "dev")
    assert result.exit_code == 0
    assert "DB_URL" in result.output


def test_keys_empty_scope_shows_message(runner, vault_file):
    result = _invoke(runner, vault_file, "keys", "nonexistent")
    assert result.exit_code == 0
    assert "No keys" in result.output


def test_list_shows_all_scopes(runner, vault_file):
    assign_scope(vault_file, "K", "dev")
    assign_scope(vault_file, "K", "prod")
    result = _invoke(runner, vault_file, "list")
    assert result.exit_code == 0
    assert "dev" in result.output
    assert "prod" in result.output


def test_list_empty_shows_message(runner, vault_file):
    result = _invoke(runner, vault_file, "list")
    assert result.exit_code == 0
    assert "No scopes" in result.output
