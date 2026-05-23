"""Tests for envault.cli_archive CLI commands."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_archive import archive_group
from envault.env_archive import archive_key
from envault.vault import Vault

PASSWORD = "test-password"


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_file(tmp_path):
    p = tmp_path / "test.vault"
    v = Vault(str(p), PASSWORD)
    v.set("API_KEY", "supersecret")
    v.set("DB_URL", "postgres://localhost/db")
    return p


def _invoke(runner, vault_file, *args, input_text=None):
    return runner.invoke(
        archive_group,
        [*args, "--vault", str(vault_file)],
        input=input_text,
        catch_exceptions=False,
    )


def test_move_archives_key(runner, vault_file):
    result = runner.invoke(
        archive_group,
        ["move", "API_KEY", "--vault", str(vault_file), "--password", PASSWORD],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "Archived 'API_KEY'" in result.output


def test_move_removes_from_vault(runner, vault_file):
    runner.invoke(
        archive_group,
        ["move", "API_KEY", "--vault", str(vault_file), "--password", PASSWORD],
        catch_exceptions=False,
    )
    v = Vault(str(vault_file), PASSWORD)
    assert v.get("API_KEY") is None


def test_move_missing_key_exits_nonzero(runner, vault_file):
    result = runner.invoke(
        archive_group,
        ["move", "GHOST", "--vault", str(vault_file), "--password", PASSWORD],
        catch_exceptions=False,
    )
    assert result.exit_code != 0


def test_restore_brings_key_back(runner, vault_file):
    archive_key(str(vault_file), "EXTRA", "restored_value")
    result = runner.invoke(
        archive_group,
        ["restore", "EXTRA", "--vault", str(vault_file), "--password", PASSWORD],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    v = Vault(str(vault_file), PASSWORD)
    assert v.get("EXTRA") == "restored_value"


def test_restore_missing_key_exits_nonzero(runner, vault_file):
    result = runner.invoke(
        archive_group,
        ["restore", "NOPE", "--vault", str(vault_file), "--password", PASSWORD],
        catch_exceptions=False,
    )
    assert result.exit_code != 0


def test_list_shows_archived_entries(runner, vault_file):
    archive_key(str(vault_file), "OLD_KEY", "oldval")
    result = _invoke(runner, vault_file, "list")
    assert "OLD_KEY" in result.output


def test_list_empty_message(runner, vault_file):
    result = _invoke(runner, vault_file, "list")
    assert "No archived entries" in result.output


def test_purge_removes_archived_entry(runner, vault_file):
    archive_key(str(vault_file), "DEAD", "val")
    result = _invoke(runner, vault_file, "purge", "DEAD")
    assert result.exit_code == 0
    assert "Purged 'DEAD'" in result.output


def test_purge_missing_exits_nonzero(runner, vault_file):
    result = _invoke(runner, vault_file, "purge", "MISSING")
    assert result.exit_code != 0
