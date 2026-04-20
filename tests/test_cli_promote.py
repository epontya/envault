"""Tests for envault.cli_promote CLI commands."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_promote import promote_group
from envault.vault import Vault

PASSWORD = "test-secret"


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def src_file(tmp_path: Path) -> Path:
    p = tmp_path / "src.vault"
    v = Vault(p, PASSWORD)
    v.set("KEY_A", "value_a")
    v.set("KEY_B", "value_b")
    return p


@pytest.fixture()
def dst_file(tmp_path: Path) -> Path:
    p = tmp_path / "dst.vault"
    Vault(p, PASSWORD)  # create empty vault
    return p


def _invoke(runner: CliRunner, src: Path, dst: Path, *extra_args: str) -> object:
    return runner.invoke(
        promote_group,
        ["run", str(src), str(dst),
         "--src-password", PASSWORD,
         "--dst-password", PASSWORD,
         *extra_args],
    )


def test_promote_all_success(runner: CliRunner, src_file: Path, dst_file: Path) -> None:
    result = _invoke(runner, src_file, dst_file, "--overwrite")
    assert result.exit_code == 0
    assert "promoted" in result.output
    assert "Done:" in result.output


def test_promote_selected_key(runner: CliRunner, src_file: Path, dst_file: Path) -> None:
    result = _invoke(runner, src_file, dst_file, "-k", "KEY_A")
    assert result.exit_code == 0
    assert "KEY_A" in result.output
    assert "KEY_B" not in result.output


def test_no_overwrite_shows_skipped(runner: CliRunner, src_file: Path, dst_file: Path) -> None:
    # Pre-populate destination with KEY_A
    Vault(dst_file, PASSWORD).set("KEY_A", "old_value")
    result = _invoke(runner, src_file, dst_file)
    assert result.exit_code == 0
    assert "skipped" in result.output


def test_unknown_key_exits_nonzero(runner: CliRunner, src_file: Path, dst_file: Path) -> None:
    result = _invoke(runner, src_file, dst_file, "-k", "GHOST")
    assert result.exit_code != 0


def test_empty_source_reports_no_entries(
    runner: CliRunner, tmp_path: Path, dst_file: Path
) -> None:
    empty = tmp_path / "empty.vault"
    Vault(empty, PASSWORD)  # create empty vault
    result = _invoke(runner, empty, dst_file)
    assert result.exit_code == 0
    assert "No entries" in result.output
