"""Tests for envault.lock and envault.cli_lock."""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.lock import (
    LockError,
    assert_unlocked,
    is_locked,
    lock_info,
    lock_vault,
    unlock_vault,
)
from envault.cli_lock import lock_group


@pytest.fixture()
def vault_file(tmp_path: Path) -> Path:
    p = tmp_path / "test.vault"
    p.write_text("{}")
    return p


# ── unit tests ────────────────────────────────────────────────────────────────

def test_lock_creates_lock_file(vault_file: Path) -> None:
    lock_vault(vault_file)
    assert (vault_file.parent / ".vault.lock").exists()


def test_lock_record_fields(vault_file: Path) -> None:
    before = time.time()
    record = lock_vault(vault_file, reason="test")
    assert record["reason"] == "test"
    assert record["vault"] == vault_file.name
    assert record["locked_at"] >= before


def test_is_locked_true_after_lock(vault_file: Path) -> None:
    lock_vault(vault_file)
    assert is_locked(vault_file) is True


def test_is_locked_false_before_lock(vault_file: Path) -> None:
    assert is_locked(vault_file) is False


def test_unlock_returns_true_when_locked(vault_file: Path) -> None:
    lock_vault(vault_file)
    assert unlock_vault(vault_file) is True
    assert is_locked(vault_file) is False


def test_unlock_returns_false_when_not_locked(vault_file: Path) -> None:
    assert unlock_vault(vault_file) is False


def test_lock_info_returns_none_when_not_locked(vault_file: Path) -> None:
    assert lock_info(vault_file) is None


def test_lock_info_returns_dict_when_locked(vault_file: Path) -> None:
    lock_vault(vault_file, reason="ci")
    info = lock_info(vault_file)
    assert isinstance(info, dict)
    assert info["reason"] == "ci"


def test_assert_unlocked_raises_when_locked(vault_file: Path) -> None:
    lock_vault(vault_file)
    with pytest.raises(LockError, match="locked"):
        assert_unlocked(vault_file)


def test_assert_unlocked_passes_when_not_locked(vault_file: Path) -> None:
    assert_unlocked(vault_file)  # should not raise


def test_corrupt_lock_file_raises(vault_file: Path) -> None:
    (vault_file.parent / ".vault.lock").write_text("not-json")
    with pytest.raises(LockError, match="Corrupt"):
        lock_info(vault_file)


# ── CLI tests ─────────────────────────────────────────────────────────────────

@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner(mix_stderr=False)


def _invoke(runner: CliRunner, vault_file: Path, *args: str):
    return runner.invoke(lock_group, [*args, "--vault", str(vault_file)])


def test_cli_lock_on(runner: CliRunner, vault_file: Path) -> None:
    result = _invoke(runner, vault_file, "on")
    assert result.exit_code == 0
    assert "locked" in result.output
    assert is_locked(vault_file)


def test_cli_lock_off(runner: CliRunner, vault_file: Path) -> None:
    lock_vault(vault_file)
    result = _invoke(runner, vault_file, "off")
    assert result.exit_code == 0
    assert "unlocked" in result.output
    assert not is_locked(vault_file)


def test_cli_status_locked(runner: CliRunner, vault_file: Path) -> None:
    lock_vault(vault_file, reason="deploy")
    result = _invoke(runner, vault_file, "status")
    assert result.exit_code == 0
    assert "locked" in result.output
    assert "deploy" in result.output


def test_cli_status_unlocked(runner: CliRunner, vault_file: Path) -> None:
    result = _invoke(runner, vault_file, "status")
    assert result.exit_code == 0
    assert "unlocked" in result.output


def test_cli_lock_on_nonexistent_vault(runner: CliRunner, tmp_path: Path) -> None:
    missing = tmp_path / "ghost.vault"
    result = runner.invoke(lock_group, ["on", "--vault", str(missing)])
    assert result.exit_code != 0
