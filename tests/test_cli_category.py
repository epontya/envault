"""Tests for envault.cli_category."""
import pytest
from click.testing import CliRunner

from envault.cli_category import category_group


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_file(tmp_path):
    return str(tmp_path / "test.vault")


def _invoke(runner, vault_file, *args):
    return runner.invoke(
        category_group,
        list(args),
        obj={"vault_path": vault_file},
        catch_exceptions=False,
    )


def test_assign_success(runner, vault_file):
    result = _invoke(runner, vault_file, "assign", "DB_HOST", "database")
    assert result.exit_code == 0
    assert "database" in result.output


def test_get_after_assign(runner, vault_file):
    _invoke(runner, vault_file, "assign", "API_KEY", "auth")
    result = _invoke(runner, vault_file, "get", "API_KEY")
    assert result.exit_code == 0
    assert "auth" in result.output


def test_get_missing_key_exits_nonzero(runner, vault_file):
    result = _invoke(runner, vault_file, "get", "MISSING")
    assert result.exit_code != 0


def test_remove_success(runner, vault_file):
    _invoke(runner, vault_file, "assign", "X", "misc")
    result = _invoke(runner, vault_file, "remove", "X")
    assert result.exit_code == 0
    assert "removed" in result.output.lower()


def test_remove_missing_exits_nonzero(runner, vault_file):
    result = _invoke(runner, vault_file, "remove", "GHOST")
    assert result.exit_code != 0


def test_list_all_categories(runner, vault_file):
    _invoke(runner, vault_file, "assign", "A", "alpha")
    _invoke(runner, vault_file, "assign", "B", "beta")
    result = _invoke(runner, vault_file, "list")
    assert result.exit_code == 0
    assert "alpha" in result.output
    assert "beta" in result.output


def test_list_by_category_filter(runner, vault_file):
    _invoke(runner, vault_file, "assign", "DB_HOST", "database")
    _invoke(runner, vault_file, "assign", "API_KEY", "auth")
    result = _invoke(runner, vault_file, "list", "--category", "database")
    assert result.exit_code == 0
    assert "DB_HOST" in result.output
    assert "API_KEY" not in result.output


def test_list_empty_vault(runner, vault_file):
    result = _invoke(runner, vault_file, "list")
    assert result.exit_code == 0
    assert "No categories" in result.output
