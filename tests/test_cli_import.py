"""Tests for the CLI import commands."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli import cli
from envault.cli_import import import_group


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def vault_file(tmp_path: Path) -> Path:
    return tmp_path / "vault.enc"


def _invoke(runner: CliRunner, vault_file: Path, *args: str):
    # Register import_group on the main cli for testing
    if "import" not in [c.name for c in cli.commands.values() if hasattr(c, "name")]:
        try:
            cli.add_command(import_group)
        except Exception:
            pass
    return runner.invoke(
        cli,
        ["--vault", str(vault_file), "--password", "testpass", "import"] + list(args),
        catch_exceptions=False,
    )


def test_import_dotenv_creates_entries(runner: CliRunner, vault_file: Path, tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("FOO=bar\nBAZ=qux\n")
    result = _invoke(runner, vault_file, "dotenv", str(env_file))
    assert result.exit_code == 0
    assert "Imported 2" in result.output


def test_import_dotenv_no_overwrite_skips(runner: CliRunner, vault_file: Path, tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("FOO=original\n")
    _invoke(runner, vault_file, "dotenv", str(env_file))
    env_file.write_text("FOO=new\n")
    result = _invoke(runner, vault_file, "dotenv", str(env_file))
    assert "skipped 1" in result.output


def test_import_dotenv_overwrite_replaces(runner: CliRunner, vault_file: Path, tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("FOO=original\n")
    _invoke(runner, vault_file, "dotenv", str(env_file))
    env_file.write_text("FOO=updated\n")
    result = _invoke(runner, vault_file, "dotenv", "--overwrite", str(env_file))
    assert "Imported 1" in result.output
    assert "skipped 0" in result.output


def test_import_json_creates_entries(runner: CliRunner, vault_file: Path, tmp_path: Path) -> None:
    json_file = tmp_path / "vars.json"
    json_file.write_text(json.dumps({"X": "1", "Y": "2"}))
    result = _invoke(runner, vault_file, "json", str(json_file))
    assert result.exit_code == 0
    assert "Imported 2" in result.output


def test_import_json_invalid_file_shows_error(runner: CliRunner, vault_file: Path, tmp_path: Path) -> None:
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("not valid json")
    result = runner.invoke(
        cli,
        ["--vault", str(vault_file), "--password", "testpass", "import", "json", str(bad_file)],
    )
    assert result.exit_code != 0


def test_import_env_with_prefix(runner: CliRunner, vault_file: Path, monkeypatch) -> None:
    monkeypatch.setenv("MYAPP_TOKEN", "abc123")
    monkeypatch.setenv("OTHER_THING", "ignored")
    result = _invoke(runner, vault_file, "env", "--prefix", "MYAPP_")
    assert result.exit_code == 0
    assert "Imported" in result.output
