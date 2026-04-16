"""CLI tests for env_group commands."""
from __future__ import annotations
import pytest
from click.testing import CliRunner
from pathlib import Path
from envault.cli_env_group import group_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path) -> str:
    return str(tmp_path / "vault.db")


def _invoke(runner, vault_file, *args):
    return runner.invoke(group_group, [*args[0:1], vault_file, *args[1:]])


def test_create_success(runner, vault_file):
    result = runner.invoke(group_group, ["create", vault_file, "backend", "DB_URL", "SECRET"])
    assert result.exit_code == 0
    assert "backend" in result.output
    assert "DB_URL" in result.output


def test_create_no_keys_exits_nonzero(runner, vault_file):
    result = runner.invoke(group_group, ["create", vault_file, "backend"])
    assert result.exit_code != 0


def test_get_existing_group(runner, vault_file):
    runner.invoke(group_group, ["create", vault_file, "g", "A", "B"])
    result = runner.invoke(group_group, ["get", vault_file, "g"])
    assert result.exit_code == 0
    assert "A" in result.output
    assert "B" in result.output


def test_get_missing_group_exits_nonzero(runner, vault_file):
    result = runner.invoke(group_group, ["get", vault_file, "ghost"])
    assert result.exit_code != 0


def test_remove_existing_group(runner, vault_file):
    runner.invoke(group_group, ["create", vault_file, "g", "X"])
    result = runner.invoke(group_group, ["remove", vault_file, "g"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_missing_group_exits_nonzero(runner, vault_file):
    result = runner.invoke(group_group, ["remove", vault_file, "ghost"])
    assert result.exit_code != 0


def test_list_empty(runner, vault_file):
    result = runner.invoke(group_group, ["list", vault_file])
    assert result.exit_code == 0
    assert "No groups" in result.output


def test_list_shows_groups(runner, vault_file):
    runner.invoke(group_group, ["create", vault_file, "alpha", "K1"])
    runner.invoke(group_group, ["create", vault_file, "beta", "K2"])
    result = runner.invoke(group_group, ["list", vault_file])
    assert "alpha" in result.output
    assert "beta" in result.output


def test_add_key_success(runner, vault_file):
    runner.invoke(group_group, ["create", vault_file, "g", "A"])
    result = runner.invoke(group_group, ["add-key", vault_file, "g", "B"])
    assert result.exit_code == 0
    assert "B" in result.output


def test_add_key_missing_group_exits_nonzero(runner, vault_file):
    result = runner.invoke(group_group, ["add-key", vault_file, "ghost", "K"])
    assert result.exit_code != 0


def test_remove_key_success(runner, vault_file):
    runner.invoke(group_group, ["create", vault_file, "g", "A", "B"])
    result = runner.invoke(group_group, ["remove-key", vault_file, "g", "A"])
    assert result.exit_code == 0


def test_remove_key_missing_exits_nonzero(runner, vault_file):
    runner.invoke(group_group, ["create", vault_file, "g", "A"])
    result = runner.invoke(group_group, ["remove-key", vault_file, "g", "Z"])
    assert result.exit_code != 0
