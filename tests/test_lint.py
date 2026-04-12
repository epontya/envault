"""Tests for envault.lint."""

from __future__ import annotations

import pytest

from envault.vault import Vault
from envault.lint import lint_vault, LintResult, LintIssue


PASSWORD = "test-password"


@pytest.fixture()
def vault(tmp_path):
    v = Vault(str(tmp_path / "vault.db"), PASSWORD)
    return v


def _populate(vault: Vault, entries: dict) -> None:
    for k, v in entries.items():
        vault.set(k, v, PASSWORD)


def test_no_issues_for_clean_vault(vault):
    _populate(vault, {"DATABASE_URL": "postgres://localhost/db", "API_KEY": "abc123"})
    result = lint_vault(vault, PASSWORD)
    assert not result.issues


def test_empty_value_produces_warning(vault):
    _populate(vault, {"EMPTY_VAR": ""})
    result = lint_vault(vault, PASSWORD)
    assert any(i.severity == "warning" and "EMPTY_VAR" in i.message for i in result.issues)


def test_invalid_key_produces_error(vault):
    _populate(vault, {"123INVALID": "value"})
    result = lint_vault(vault, PASSWORD)
    assert any(i.severity == "error" and "123INVALID" in i.message for i in result.issues)


def test_placeholder_value_produces_warning(vault):
    _populate(vault, {"SECRET": "${MY_SECRET}"})
    result = lint_vault(vault, PASSWORD)
    assert any(i.severity == "warning" and "SECRET" in i.message for i in result.issues)


def test_angle_bracket_placeholder_produces_warning(vault):
    _populate(vault, {"TOKEN": "<YOUR_TOKEN>"})
    result = lint_vault(vault, PASSWORD)
    assert any(i.severity == "warning" and "TOKEN" in i.message for i in result.issues)


def test_case_insensitive_duplicate_produces_warning(vault):
    _populate(vault, {"db_host": "localhost", "DB_HOST": "remotehost"})
    result = lint_vault(vault, PASSWORD)
    warnings = [i for i in result.issues if i.severity == "warning"]
    assert any("case-insensitive duplicate" in w.message for w in warnings)


def test_has_errors_flag(vault):
    _populate(vault, {"bad key!": "value"})
    result = lint_vault(vault, PASSWORD)
    assert result.has_errors


def test_has_warnings_flag(vault):
    _populate(vault, {"EMPTY": ""})
    result = lint_vault(vault, PASSWORD)
    assert result.has_warnings


def test_summary_format(vault):
    _populate(vault, {"bad key!": ""})
    result = lint_vault(vault, PASSWORD)
    summary = result.summary()
    assert "error" in summary
    assert "warning" in summary


def test_empty_vault_has_no_issues(vault):
    result = lint_vault(vault, PASSWORD)
    assert result.issues == []
