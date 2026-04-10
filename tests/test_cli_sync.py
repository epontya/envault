"""Tests for envault.cli_sync."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli import cli
from envault.cli_sync import sync_group
from envault.vault import Vault

PASSWORD = "cli-sync-secret"


@pytest.fixture(autouse=True)
def _register_sync(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Attach the sync group to the main CLI for the duration of each test."""
    cli.add_command(sync_group)
    yield
    # Click stores commands in a dict; remove after test to avoid pollution
    cli.commands.pop("sync", None)  # type: ignore[attr-defined]


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner(mix_stderr=False)


@pytest.fixture()
def vault_file(tmp_path: Path) -> Path:
    path = tmp_path / "test.vault"
    v = Vault(path, PASSWORD)
    v.set("ALPHA", "one")
    v.set("BETA", "two")
    return path


def _invoke(runner: CliRunner, *args: str, vault: Path) -> object:
    return runner.invoke(
        cli,
        ["sync", *args, "--vault-file", str(vault), "--password", PASSWORD],
        catch_exceptions=False,
    )


def test_push_creates_file(runner: CliRunner, vault_file: Path, tmp_path: Path) -> None:
    dest = tmp_path / "pushed.sync"
    result = _invoke(runner, "push", str(dest), vault=vault_file)
    assert result.exit_code == 0
    assert dest.exists()
    assert "pushed" in result.output.lower()


def test_pull_merges_keys(runner: CliRunner, vault_file: Path, tmp_path: Path) -> None:
    dest = tmp_path / "pushed.sync"
    _invoke(runner, "push", str(dest), vault=vault_file)

    new_vault_path = tmp_path / "new.vault"
    result = runner.invoke(
        cli,
        ["sync", "pull", str(dest), "--vault-file", str(new_vault_path), "--password", PASSWORD],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "2" in result.output

    new_vault = Vault(new_vault_path, PASSWORD)
    assert new_vault.get("ALPHA") == "one"
    assert new_vault.get("BETA") == "two"


def test_pull_no_overwrite(runner: CliRunner, vault_file: Path, tmp_path: Path) -> None:
    dest = tmp_path / "pushed.sync"
    _invoke(runner, "push", str(dest), vault=vault_file)

    # Destination vault already has ALPHA set to a different value
    target = tmp_path / "target.vault"
    tv = Vault(target, PASSWORD)
    tv.set("ALPHA", "original")

    runner.invoke(
        cli,
        [
            "sync", "pull", str(dest),
            "--vault-file", str(target),
            "--no-overwrite",
            "--password", PASSWORD,
        ],
        catch_exceptions=False,
    )
    assert tv.get("ALPHA") == "original"
    assert tv.get("BETA") == "two"
