"""Tests for envault.audit and envault.cli_audit."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.audit import AuditLog
from envault.cli_audit import audit_group


@pytest.fixture()
def log_file(tmp_path: Path) -> Path:
    return tmp_path / "audit.log"


@pytest.fixture()
def al(log_file: Path) -> AuditLog:
    return AuditLog(log_file)


def test_record_creates_file(al: AuditLog, log_file: Path) -> None:
    al.record("set", "/tmp/vault.enc", key="API_KEY")
    assert log_file.exists()


def test_record_entry_fields(al: AuditLog, log_file: Path) -> None:
    al.record("get", "/tmp/vault.enc", key="DB_URL", success=True)
    lines = log_file.read_text().splitlines()
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["action"] == "get"
    assert entry["key"] == "DB_URL"
    assert entry["success"] is True
    assert "timestamp" in entry


def test_record_includes_vault_path(al: AuditLog, log_file: Path) -> None:
    """Ensure the vault path is stored in each audit entry."""
    al.record("set", "/tmp/vault.enc", key="API_KEY")
    entry = json.loads(log_file.read_text().splitlines()[0])
    assert entry["vault"] == "/tmp/vault.enc"


def test_multiple_records_appended(al: AuditLog) -> None:
    al.record("set", "/v", key="A")
    al.record("delete", "/v", key="B", success=False)
    entries = al.read()
    assert len(entries) == 2
    assert entries[0]["action"] == "set"
    assert entries[1]["action"] == "delete"


def test_read_empty_log(al: AuditLog) -> None:
    assert al.read() == []


def test_read_respects_limit(al: AuditLog) -> None:
    for i in range(10):
        al.record("set", "/v", key=f"K{i}")
    entries = al.read(limit=3)
    assert len(entries) == 3


def test_read_limit_returns_most_recent(al: AuditLog) -> None:
    """read(limit=N) should return the N most recent entries."""
    for i in range(5):
        al.record("set", "/v", key=f"K{i}")
    entries = al.read(limit=2)
    assert entries[0]["key"] == "K3"
    assert entries[1]["key"] == "K4"


def test_clear_removes_entries(al: AuditLog) -> None:
    al.record("set", "/v", key="X")
    al.clear()
    assert al.read() == []


# --- CLI tests ---


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def test_cli_log_empty(runner: CliRunner, log_file: Path) -> None:
    result = runner.invoke(audit_group, ["log", "--log-file", str(log_file)])
    assert result.exit_code == 0
    assert "No audit entries found" in result.output


def test_cli_log_shows_entries(runner: CliRunner, log_file: Path) -> None:
    al = AuditLog(log_file)
    al.record("set", "/tmp/v.enc", key="SECRET")
    result = runner.invoke(audit_group, ["log", "--log-file", str(log_file)])
    assert result.exit_code == 0
    assert "set" in result.output
    assert "SECRET" in result.output


def test_cli_clear(runner: CliRunner, log_file: Path) -> None:
    al = AuditLog(log_file)
    al.record("set", "/tmp/v.enc", key="X")
    result = runner.invoke(
        audit_group, ["clear", "--log-file", str(log_file)], input="y\n"
    )
    assert result.exit_code == 0
    assert al.read() == []
