"""Tests for envault.policy."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.policy import (
    PolicyConfig,
    check_value,
    load_policy,
    save_policy,
)
from envault.cli_policy import policy_group


@pytest.fixture()
def vault_file(tmp_path: Path) -> Path:
    p = tmp_path / "test.vault"
    p.write_bytes(b"")
    return p


# --- Unit tests for check_value ---

def test_no_violations_for_default_policy():
    cfg = PolicyConfig()
    assert check_value("hello123", cfg) == []


def test_min_length_violation():
    cfg = PolicyConfig(min_length=10)
    violations = check_value("short", cfg)
    assert any(v.rule == "min_length" for v in violations)


def test_max_length_violation():
    cfg = PolicyConfig(max_length=5)
    violations = check_value("toolongvalue", cfg)
    assert any(v.rule == "max_length" for v in violations)


def test_require_uppercase_violation():
    cfg = PolicyConfig(require_uppercase=True)
    violations = check_value("alllower", cfg)
    assert any(v.rule == "require_uppercase" for v in violations)


def test_require_uppercase_passes():
    cfg = PolicyConfig(require_uppercase=True)
    assert check_value("HasUpper", cfg) == []


def test_require_digit_violation():
    cfg = PolicyConfig(require_digit=True)
    violations = check_value("NoDigitsHere", cfg)
    assert any(v.rule == "require_digit" for v in violations)


def test_require_special_violation():
    cfg = PolicyConfig(require_special=True)
    violations = check_value("NoSpecial1", cfg)
    assert any(v.rule == "require_special" for v in violations)


def test_require_special_passes():
    cfg = PolicyConfig(require_special=True)
    assert check_value("Has!Special", cfg) == []


def test_forbidden_pattern_violation():
    cfg = PolicyConfig(forbidden_patterns=[r"password"])
    violations = check_value("mypassword123", cfg)
    assert any(v.rule == "forbidden_pattern" for v in violations)


def test_forbidden_pattern_no_match():
    cfg = PolicyConfig(forbidden_patterns=[r"password"])
    assert check_value("s3cr3t!", cfg) == []


# --- Persistence tests ---

def test_save_and_load_policy(vault_file: Path):
    cfg = PolicyConfig(min_length=12, require_digit=True)
    save_policy(vault_file, cfg)
    loaded = load_policy(vault_file)
    assert loaded.min_length == 12
    assert loaded.require_digit is True


def test_load_policy_defaults_when_no_file(vault_file: Path):
    cfg = load_policy(vault_file)
    assert cfg.min_length == 8
    assert cfg.require_uppercase is False


# --- CLI tests ---

@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_set_and_show(runner, vault_file):
    result = runner.invoke(policy_group, ["set", "--vault", str(vault_file), "--min-length", "16"])
    assert result.exit_code == 0
    result = runner.invoke(policy_group, ["show", "--vault", str(vault_file)])
    assert "16" in result.output


def test_cli_check_passes(runner, vault_file):
    runner.invoke(policy_group, ["set", "--vault", str(vault_file), "--min-length", "4"])
    result = runner.invoke(policy_group, ["check", "--vault", str(vault_file), "good"])
    assert result.exit_code == 0
    assert "OK" in result.output


def test_cli_check_fails(runner, vault_file):
    runner.invoke(policy_group, ["set", "--vault", str(vault_file), "--min-length", "20"])
    result = runner.invoke(policy_group, ["check", "--vault", str(vault_file), "short"])
    assert result.exit_code != 0
