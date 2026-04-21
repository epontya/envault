"""Tests for envault.cli_chain CLI commands."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_chain import chain_group
from envault.vault import Vault

PASSWORD = "cli-chain-pw"


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_file(tmp_path: Path) -> Path:
    vp = tmp_path / "v.vault"
    v = Vault(vp, PASSWORD)
    v.set("PRIMARY_KEY", "pval")
    v.set("CONFLICT", "primary")
    return vp


@pytest.fixture()
def linked_file(tmp_path: Path) -> Path:
    vp = tmp_path / "linked.vault"
    v = Vault(vp, PASSWORD)
    v.set("LINKED_KEY", "lval")
    v.set("CONFLICT", "linked")
    return vp


def _invoke(runner, vault_file, *args, input_text=None):
    return runner.invoke(
        chain_group,
        [*args],
        env={"ENVAULT_VAULT": str(vault_file)},
        input=input_text,
        catch_exceptions=False,
    )


def test_add_success(runner, vault_file, linked_file):
    result = _invoke(runner, vault_file, "add", str(vault_file), str(linked_file))
    assert result.exit_code == 0
    assert "Chain updated" in result.output


def test_add_duplicate_exits_nonzero(runner, vault_file, linked_file):
    _invoke(runner, vault_file, "add", str(vault_file), str(linked_file))
    result = _invoke(runner, vault_file, "add", str(vault_file), str(linked_file))
    assert result.exit_code != 0


def test_list_empty(runner, vault_file):
    result = _invoke(runner, vault_file, "list", str(vault_file))
    assert result.exit_code == 0
    assert "No vaults" in result.output


def test_list_shows_linked(runner, vault_file, linked_file):
    _invoke(runner, vault_file, "add", str(vault_file), str(linked_file))
    result = _invoke(runner, vault_file, "list", str(vault_file))
    assert result.exit_code == 0
    assert str(linked_file) in result.output


def test_remove_success(runner, vault_file, linked_file):
    _invoke(runner, vault_file, "add", str(vault_file), str(linked_file))
    result = _invoke(runner, vault_file, "remove", str(vault_file), str(linked_file))
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_remove_missing_exits_nonzero(runner, vault_file, linked_file):
    result = _invoke(runner, vault_file, "remove", str(vault_file), str(linked_file))
    assert result.exit_code != 0


def test_get_primary_key(runner, vault_file, linked_file):
    _invoke(runner, vault_file, "add", str(vault_file), str(linked_file))
    result = runner.invoke(
        chain_group,
        ["get", str(vault_file), "PRIMARY_KEY", "--password", PASSWORD],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "pval" in result.output


def test_get_missing_key_exits_nonzero(runner, vault_file):
    result = runner.invoke(
        chain_group,
        ["get", str(vault_file), "NO_SUCH_KEY", "--password", PASSWORD],
        catch_exceptions=False,
    )
    assert result.exit_code != 0
