"""Tests for the envault CLI commands."""

import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.cli import cli


PASSWORD = "test-secret-password"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path):
    return str(tmp_path / "test.vault")


def invoke(runner, args, password=PASSWORD, input_text=None):
    """Helper to invoke CLI with vault path and password options."""
    full_args = args
    if input_text is None:
        input_text = f"{password}\n{password}\n"
    return runner.invoke(cli, full_args, input=input_text, catch_exceptions=False)


def test_set_and_get(runner, vault_file):
    result = invoke(runner, ["set", "MY_KEY", "my_value", "--vault", vault_file])
    assert result.exit_code == 0
    assert "Set 'MY_KEY'" in result.output

    result = invoke(runner, ["get", "MY_KEY", "--vault", vault_file], input_text=f"{PASSWORD}\n")
    assert result.exit_code == 0
    assert "my_value" in result.output


def test_get_missing_key_exits_nonzero(runner, vault_file):
    invoke(runner, ["set", "SOME_KEY", "val", "--vault", vault_file])
    result = invoke(runner, ["get", "MISSING", "--vault", vault_file], input_text=f"{PASSWORD}\n")
    assert result.exit_code != 0


def test_delete_existing_key(runner, vault_file):
    invoke(runner, ["set", "DEL_KEY", "del_value", "--vault", vault_file])
    result = invoke(runner, ["delete", "DEL_KEY", "--vault", vault_file], input_text=f"{PASSWORD}\n")
    assert result.exit_code == 0
    assert "Deleted 'DEL_KEY'" in result.output


def test_delete_missing_key_exits_nonzero(runner, vault_file):
    invoke(runner, ["set", "SOME_KEY", "val", "--vault", vault_file])
    result = invoke(runner, ["delete", "GHOST", "--vault", vault_file], input_text=f"{PASSWORD}\n")
    assert result.exit_code != 0


def test_list_empty_vault(runner, vault_file):
    invoke(runner, ["set", "INIT", "x", "--vault", vault_file])
    invoke(runner, ["delete", "INIT", "--vault", vault_file], input_text=f"{PASSWORD}\n")
    result = invoke(runner, ["list", "--vault", vault_file], input_text=f"{PASSWORD}\n")
    assert result.exit_code == 0
    assert "empty" in result.output.lower()


def test_list_shows_keys(runner, vault_file):
    invoke(runner, ["set", "ALPHA", "1", "--vault", vault_file])
    invoke(runner, ["set", "BETA", "2", "--vault", vault_file])
    result = invoke(runner, ["list", "--vault", vault_file], input_text=f"{PASSWORD}\n")
    assert result.exit_code == 0
    assert "ALPHA" in result.output
    assert "BETA" in result.output


def test_wrong_password_on_get(runner, vault_file):
    invoke(runner, ["set", "KEY", "value", "--vault", vault_file])
    with pytest.raises(ValueError):
        runner.invoke(
            cli,
            ["get", "KEY", "--vault", vault_file],
            input="wrongpassword\n",
            catch_exceptions=False,
        )
