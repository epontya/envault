"""Integration tests for the profile CLI commands."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envault.cli_profiles import profile_group
from envault.profiles import ProfileManager


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def pm_path(tmp_path: Path) -> Path:
    return tmp_path / "profiles.json"


def _invoke(runner: CliRunner, pm_path: Path, *args: str):
    """Invoke profile_group with a patched ProfileManager."""
    with patch("envault.cli_profiles._pm", return_value=ProfileManager(profiles_path=pm_path)):
        return runner.invoke(profile_group, list(args), catch_exceptions=False)


def test_add_profile(runner: CliRunner, pm_path: Path, tmp_path: Path) -> None:
    vault = tmp_path / "dev.vault"
    result = _invoke(runner, pm_path, "add", "dev", str(vault))
    assert result.exit_code == 0
    assert "dev" in result.output


def test_list_empty(runner: CliRunner, pm_path: Path) -> None:
    result = _invoke(runner, pm_path, "list")
    assert result.exit_code == 0
    assert "No profiles" in result.output


def test_list_shows_profiles(runner: CliRunner, pm_path: Path, tmp_path: Path) -> None:
    pm = ProfileManager(profiles_path=pm_path)
    pm.add("dev", tmp_path / "dev.vault")
    pm.add("prod", tmp_path / "prod.vault")
    result = _invoke(runner, pm_path, "list")
    assert "dev" in result.output
    assert "prod" in result.output


def test_remove_existing(runner: CliRunner, pm_path: Path, tmp_path: Path) -> None:
    pm = ProfileManager(profiles_path=pm_path)
    pm.add("dev", tmp_path / "dev.vault")
    result = _invoke(runner, pm_path, "remove", "dev")
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_missing_exits_nonzero(runner: CliRunner, pm_path: Path) -> None:
    result = _invoke(runner, pm_path, "remove", "ghost")
    assert result.exit_code != 0


def test_rename_profile(runner: CliRunner, pm_path: Path, tmp_path: Path) -> None:
    pm = ProfileManager(profiles_path=pm_path)
    pm.add("old", tmp_path / "old.vault")
    result = _invoke(runner, pm_path, "rename", "old", "new")
    assert result.exit_code == 0
    assert "new" in result.output


def test_show_profile(runner: CliRunner, pm_path: Path, tmp_path: Path) -> None:
    vault = tmp_path / "dev.vault"
    pm = ProfileManager(profiles_path=pm_path)
    pm.add("dev", vault)
    result = _invoke(runner, pm_path, "show", "dev")
    assert result.exit_code == 0
    assert str(vault) in result.output


def test_show_missing_exits_nonzero(runner: CliRunner, pm_path: Path) -> None:
    result = _invoke(runner, pm_path, "show", "nope")
    assert result.exit_code != 0
