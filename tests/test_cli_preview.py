"""Tests for envault.cli_preview CLI commands."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_preview import preview_group
from envault.vault import Vault


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_file(tmp_path):
    path = tmp_path / "test.vault"
    v = Vault(str(path), password="testpass")
    v.set("API_KEY", "topsecret")
    v.set("APP_NAME", "envault")
    v.set("PORT", "9000")
    return str(path)


def _invoke(runner, vault_file, *args, password="testpass"):
    return runner.invoke(
        preview_group,
        [*args, "--vault", vault_file, "--password", password],
        catch_exceptions=False,
    )


def test_show_lists_all_keys(runner, vault_file):
    result = _invoke(runner, vault_file, "show")
    assert result.exit_code == 0
    assert "APP_NAME" in result.output
    assert "PORT" in result.output


def test_show_redacts_sensitive_by_default(runner, vault_file):
    result = _invoke(runner, vault_file, "show")
    assert result.exit_code == 0
    assert "topsecret" not in result.output
    assert "[sensitive]" in result.output


def test_show_reveal_exposes_sensitive(runner, vault_file):
    result = _invoke(runner, vault_file, "show", "--reveal")
    assert result.exit_code == 0
    assert "topsecret" in result.output


def test_show_wrong_password_fails(runner, vault_file):
    result = _invoke(runner, vault_file, "show", password="wrongpass")
    assert result.exit_code != 0


def test_key_shows_single_entry(runner, vault_file):
    result = _invoke(runner, vault_file, "key", "APP_NAME")
    assert result.exit_code == 0
    assert "APP_NAME" in result.output
    assert "PORT" not in result.output


def test_key_missing_exits_nonzero(runner, vault_file):
    result = _invoke(runner, vault_file, "key", "DOES_NOT_EXIST")
    assert result.exit_code != 0


def test_show_extra_pattern_marks_sensitive(runner, vault_file):
    result = _invoke(runner, vault_file, "show", "--pattern", "APP_*")
    assert result.exit_code == 0
    assert "[sensitive]" in result.output
