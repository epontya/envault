"""Tests for envault.cli_rotate."""

from __future__ import annotations

import pytest
from pathlib import Path
from click.testing import CliRunner

from envault.vault import Vault
from envault.cli_rotate import rotate_group


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def vault_file(tmp_path: Path) -> Path:
    path = tmp_path / ".envault"
    v = Vault(path, "old-pass")
    v.set("FOO", "bar")
    v.set("BAZ", "qux")
    return path


def _invoke(runner: CliRunner, vault_file: Path, old: str, new: str):
    return runner.invoke(
        rotate_group,
        [
            "run",
            "--vault", str(vault_file),
            "--old-password", old,
            "--new-password", new,
        ],
        catch_exceptions=False,
    )


def test_rotate_success_message(runner: CliRunner, vault_file: Path) -> None:
    result = _invoke(runner, vault_file, "old-pass", "new-pass")
    assert result.exit_code == 0
    assert "2" in result.output
    assert "Rotated" in result.output


def test_rotate_new_password_readable(runner: CliRunner, vault_file: Path) -> None:
    _invoke(runner, vault_file, "old-pass", "new-pass")
    v = Vault(vault_file, "new-pass")
    assert v.get("FOO") == "bar"


def test_rotate_missing_vault_exits_nonzero(runner: CliRunner, tmp_path: Path) -> None:
    result = runner.invoke(
        rotate_group,
        ["run", "--vault", str(tmp_path / "no-vault"),
         "--old-password", "x", "--new-password", "y"],
    )
    assert result.exit_code != 0


def test_rotate_wrong_old_password_exits_nonzero(runner: CliRunner, vault_file: Path) -> None:
    result = runner.invoke(
        rotate_group,
        ["run", "--vault", str(vault_file),
         "--old-password", "bad", "--new-password", "new-pass"],
    )
    assert result.exit_code != 0


def test_rotate_same_password_exits_nonzero(runner: CliRunner, vault_file: Path) -> None:
    result = runner.invoke(
        rotate_group,
        ["run", "--vault", str(vault_file),
         "--old-password", "same", "--new-password", "same"],
    )
    assert result.exit_code != 0
