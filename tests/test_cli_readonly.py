"""Tests for envault.cli_readonly CLI commands."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_readonly import readonly_group
from envault.env_readonly import protect


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path) -> str:
    return str(tmp_path / "my.vault")


def _invoke(runner, vault_file, *args):
    return runner.invoke(readonly_group, [*args, vault_file] if args[0] != "list" else ["list", vault_file])


def test_protect_success(runner, vault_file):
    result = runner.invoke(readonly_group, ["protect", vault_file, "API_KEY"])
    assert result.exit_code == 0
    assert "Protected 'API_KEY'" in result.output


def test_protect_empty_key_exits_nonzero(runner, vault_file):
    result = runner.invoke(readonly_group, ["protect", vault_file, ""])
    assert result.exit_code != 0


def test_unprotect_existing_success(runner, vault_file):
    protect(vault_file, "DB_PASS")
    result = runner.invoke(readonly_group, ["unprotect", vault_file, "DB_PASS"])
    assert result.exit_code == 0
    assert "Protection removed" in result.output


def test_unprotect_missing_exits_nonzero(runner, vault_file):
    result = runner.invoke(readonly_group, ["unprotect", vault_file, "GHOST"])
    assert result.exit_code != 0


def test_check_protected_key(runner, vault_file):
    protect(vault_file, "TOKEN")
    result = runner.invoke(readonly_group, ["check", vault_file, "TOKEN"])
    assert result.exit_code == 0
    assert "read-only" in result.output


def test_check_unprotected_key(runner, vault_file):
    result = runner.invoke(readonly_group, ["check", vault_file, "FREE"])
    assert result.exit_code == 0
    assert "writable" in result.output


def test_list_empty(runner, vault_file):
    result = runner.invoke(readonly_group, ["list", vault_file])
    assert result.exit_code == 0
    assert "No keys" in result.output


def test_list_shows_protected_keys(runner, vault_file):
    protect(vault_file, "ALPHA")
    protect(vault_file, "BETA")
    result = runner.invoke(readonly_group, ["list", vault_file])
    assert result.exit_code == 0
    assert "ALPHA" in result.output
    assert "BETA" in result.output
