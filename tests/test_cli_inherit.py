"""Tests for envault.cli_inherit."""
from __future__ import annotations

import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.vault import Vault
from envault.cli_inherit import inherit_group

PASS = "secret"


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_file(tmp_path: Path) -> Path:
    vp = tmp_path / "child.vault"
    Vault(vp, PASS).set("CHILD_KEY", "child_val")
    return vp


@pytest.fixture()
def parent_file(tmp_path: Path) -> Path:
    pp = tmp_path / "parent.vault"
    Vault(pp, PASS).set("PARENT_KEY", "parent_val")
    return pp


def _invoke(runner, vault_file, *args):
    return runner.invoke(
        inherit_group,
        ["--vault", str(vault_file), "--password", PASS, *args],
        catch_exceptions=False,
    )


def test_list_empty(runner, vault_file):
    result = runner.invoke(
        inherit_group,
        ["list", "--vault", str(vault_file), "--password", PASS],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "No parents" in result.output


def test_add_parent_success(runner, vault_file, parent_file):
    result = runner.invoke(
        inherit_group,
        ["add", str(parent_file), "--vault", str(vault_file), "--password", PASS],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "Added" in result.output


def test_add_duplicate_exits_nonzero(runner, vault_file, parent_file):
    runner.invoke(
        inherit_group,
        ["add", str(parent_file), "--vault", str(vault_file), "--password", PASS],
    )
    result = runner.invoke(
        inherit_group,
        ["add", str(parent_file), "--vault", str(vault_file), "--password", PASS],
    )
    assert result.exit_code != 0


def test_remove_parent(runner, vault_file, parent_file):
    runner.invoke(
        inherit_group,
        ["add", str(parent_file), "--vault", str(vault_file), "--password", PASS],
    )
    result = runner.invoke(
        inherit_group,
        ["remove", str(parent_file), "--vault", str(vault_file), "--password", PASS],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "removed" in result.output


def test_resolve_shows_merged_keys(runner, vault_file, parent_file):
    runner.invoke(
        inherit_group,
        ["add", str(parent_file), "--vault", str(vault_file), "--password", PASS],
    )
    result = runner.invoke(
        inherit_group,
        ["resolve", "--vault", str(vault_file), "--password", PASS],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "PARENT_KEY=parent_val" in result.output
    assert "CHILD_KEY=child_val" in result.output
