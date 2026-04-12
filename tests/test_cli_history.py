"""Tests for envault.cli_history."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_history import history_group
from envault.history import HistoryStore


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def vault_file(tmp_path: Path) -> Path:
    return tmp_path / "vault.db"


def _invoke(runner: CliRunner, vault_file: Path, *args):
    return runner.invoke(
        history_group,
        [*args, "--vault", str(vault_file)],
        catch_exceptions=False,
    )


def _store(vault_file: Path) -> HistoryStore:
    return HistoryStore(vault_file.parent / (vault_file.stem + ".history.json"))


def test_log_shows_entries(runner: CliRunner, vault_file: Path):
    hs = _store(vault_file)
    hs.record("SECRET", "hunter2")
    result = _invoke(runner, vault_file, "log", "SECRET")
    assert result.exit_code == 0
    assert "SECRET=hunter2" in result.output
    assert "SET" in result.output


def test_log_missing_key_says_no_history(runner: CliRunner, vault_file: Path):
    result = _invoke(runner, vault_file, "log", "GHOST")
    assert result.exit_code == 0
    assert "No history" in result.output


def test_all_shows_all_entries(runner: CliRunner, vault_file: Path):
    hs = _store(vault_file)
    hs.record("A", "1")
    hs.record("B", "2")
    result = _invoke(runner, vault_file, "all")
    assert result.exit_code == 0
    assert "A=1" in result.output
    assert "B=2" in result.output


def test_all_empty_says_no_history(runner: CliRunner, vault_file: Path):
    result = _invoke(runner, vault_file, "all")
    assert result.exit_code == 0
    assert "No history" in result.output


def test_clear_key_with_yes_flag(runner: CliRunner, vault_file: Path):
    hs = _store(vault_file)
    hs.record("KEY", "val1")
    hs.record("KEY", "val2")
    result = _invoke(runner, vault_file, "clear", "KEY", "--yes")
    assert result.exit_code == 0
    assert "2" in result.output
    assert hs.get("KEY") == []


def test_clear_all_with_yes_flag(runner: CliRunner, vault_file: Path):
    hs = _store(vault_file)
    hs.record("A", "1")
    hs.record("B", "2")
    result = _invoke(runner, vault_file, "clear", "--yes")
    assert result.exit_code == 0
    assert hs.all() == []


def test_delete_action_shown_in_log(runner: CliRunner, vault_file: Path):
    hs = _store(vault_file)
    hs.record("GONE", None, action="delete")
    result = _invoke(runner, vault_file, "log", "GONE")
    assert result.exit_code == 0
    assert "DELETE" in result.output
    assert "<deleted>" in result.output
