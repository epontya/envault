"""Tests for envault.cli_comment."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_comment import comment_group


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_file(tmp_path):
    return str(tmp_path / "test.vault")


def _invoke(runner, vault_file, *args):
    return runner.invoke(comment_group, ["--vault", vault_file, *args])


def test_set_success(runner, vault_file):
    result = _invoke(runner, vault_file, "set", "DB_HOST", "Primary DB")
    assert result.exit_code == 0
    assert "DB_HOST" in result.output


def test_get_after_set(runner, vault_file):
    _invoke(runner, vault_file, "set", "MY_KEY", "my annotation")
    result = _invoke(runner, vault_file, "get", "MY_KEY")
    assert result.exit_code == 0
    assert "my annotation" in result.output


def test_get_missing_key_exits_nonzero(runner, vault_file):
    result = _invoke(runner, vault_file, "get", "MISSING")
    assert result.exit_code != 0


def test_remove_existing_success(runner, vault_file):
    _invoke(runner, vault_file, "set", "K", "note")
    result = _invoke(runner, vault_file, "remove", "K")
    assert result.exit_code == 0
    assert "removed" in result.output.lower()


def test_remove_missing_exits_nonzero(runner, vault_file):
    result = _invoke(runner, vault_file, "remove", "NOPE")
    assert result.exit_code != 0


def test_list_empty(runner, vault_file):
    result = _invoke(runner, vault_file, "list")
    assert result.exit_code == 0
    assert "No comments" in result.output


def test_list_shows_entries(runner, vault_file):
    _invoke(runner, vault_file, "set", "AAA", "first")
    _invoke(runner, vault_file, "set", "BBB", "second")
    result = _invoke(runner, vault_file, "list")
    assert result.exit_code == 0
    assert "AAA" in result.output
    assert "BBB" in result.output
