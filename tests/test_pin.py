"""Tests for envault.pin and envault.cli_pin."""

from __future__ import annotations

import time
from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.pin import PINError, PINStore
from envault.cli_pin import pin_group


@pytest.fixture()
def pin_file(tmp_path: Path) -> Path:
    return tmp_path / "pin_session.json"


@pytest.fixture()
def store(pin_file: Path) -> PINStore:
    return PINStore(pin_file)


# --- Unit tests ---

def test_set_and_unlock(store: PINStore) -> None:
    store.set_pin("1234", "s3cr3t")
    assert store.unlock("1234") == "s3cr3t"


def test_wrong_pin_raises(store: PINStore) -> None:
    store.set_pin("1234", "s3cr3t")
    with pytest.raises(PINError, match="Incorrect PIN"):
        store.unlock("0000")


def test_short_pin_raises(store: PINStore) -> None:
    with pytest.raises(PINError, match="at least 4 digits"):
        store.set_pin("12", "s3cr3t")


def test_non_digit_pin_raises(store: PINStore) -> None:
    with pytest.raises(PINError, match="at least 4 digits"):
        store.set_pin("abcd", "s3cr3t")


def test_no_pin_set_raises(store: PINStore) -> None:
    with pytest.raises(PINError, match="No PIN"):
        store.unlock("1234")


def test_clear_removes_session(store: PINStore) -> None:
    store.set_pin("1234", "s3cr3t")
    store.clear()
    assert not store.is_set()


def test_is_set_true_after_set(store: PINStore) -> None:
    store.set_pin("1234", "s3cr3t")
    assert store.is_set() is True


def test_expired_session_raises(store: PINStore, monkeypatch: pytest.MonkeyPatch) -> None:
    store.set_pin("1234", "s3cr3t")
    monkeypatch.setattr(time, "time", lambda: time.time() + 7201)
    with pytest.raises(PINError, match="expired"):
        store.unlock("1234")


# --- CLI tests ---

@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def _invoke(runner: CliRunner, pin_file: Path, *args: str) -> object:
    return runner.invoke(pin_group, ["--pin-file", str(pin_file), *args])


def test_cli_set_and_status(runner: CliRunner, pin_file: Path) -> None:
    result = runner.invoke(pin_group, ["set", "--pin-file", str(pin_file), "1234", "--password", "s3cr3t"])
    assert result.exit_code == 0
    assert "PIN set" in result.output
    result2 = runner.invoke(pin_group, ["status", "--pin-file", str(pin_file)])
    assert "active" in result2.output


def test_cli_clear(runner: CliRunner, pin_file: Path) -> None:
    runner.invoke(pin_group, ["set", "--pin-file", str(pin_file), "1234", "--password", "pw"])
    result = runner.invoke(pin_group, ["clear", "--pin-file", str(pin_file)])
    assert result.exit_code == 0
    assert "cleared" in result.output


def test_cli_short_pin_exits_nonzero(runner: CliRunner, pin_file: Path) -> None:
    result = runner.invoke(pin_group, ["set", "--pin-file", str(pin_file), "12", "--password", "pw"])
    assert result.exit_code != 0
