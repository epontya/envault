"""Tests for envault.env_validate."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.env_validate import (
    ValidationError,
    ValidationResult,
    ValidationIssue,
    add_rule,
    load_rules,
    remove_rule,
    validate_entries,
)


@pytest.fixture()
def vpath(tmp_path: Path) -> Path:
    return tmp_path / "test.vault"


def test_load_rules_missing_file_returns_empty(vpath):
    assert load_rules(vpath) == {}


def test_add_rule_creates_file(vpath):
    add_rule(vpath, "PORT", "type", "int")
    rules_file = vpath.with_suffix(".validate.json")
    assert rules_file.exists()


def test_add_and_load_rule(vpath):
    add_rule(vpath, "PORT", "type", "int")
    rules = load_rules(vpath)
    assert rules["PORT"]["type"] == "int"


def test_add_multiple_rules_same_key(vpath):
    add_rule(vpath, "PORT", "type", "int")
    add_rule(vpath, "PORT", "nonempty", "true")
    rules = load_rules(vpath)
    assert "type" in rules["PORT"]
    assert "nonempty" in rules["PORT"]


def test_add_invalid_rule_type_raises(vpath):
    with pytest.raises(ValidationError, match="Unknown rule type"):
        add_rule(vpath, "KEY", "unknown", "value")


def test_remove_existing_rule(vpath):
    add_rule(vpath, "KEY", "type", "int")
    assert remove_rule(vpath, "KEY") is True
    assert load_rules(vpath) == {}


def test_remove_missing_rule_returns_false(vpath):
    assert remove_rule(vpath, "MISSING") is False


def test_validate_int_type_passes(vpath):
    add_rule(vpath, "PORT", "type", "int")
    result = validate_entries({"PORT": "8080"}, vpath)
    assert not result.has_errors()


def test_validate_int_type_fails(vpath):
    add_rule(vpath, "PORT", "type", "int")
    result = validate_entries({"PORT": "notanint"}, vpath)
    assert result.has_errors()
    assert any(i.rule == "type" for i in result.issues)


def test_validate_float_type_passes(vpath):
    add_rule(vpath, "RATIO", "type", "float")
    result = validate_entries({"RATIO": "3.14"}, vpath)
    assert not result.has_errors()


def test_validate_bool_type_passes(vpath):
    add_rule(vpath, "FLAG", "type", "bool")
    for val in ("true", "false", "1", "0", "yes", "no"):
        result = validate_entries({"FLAG": val}, vpath)
        assert not result.has_errors(), f"Expected pass for '{val}'"


def test_validate_bool_type_fails(vpath):
    add_rule(vpath, "FLAG", "type", "bool")
    result = validate_entries({"FLAG": "maybe"}, vpath)
    assert result.has_errors()


def test_validate_regex_passes(vpath):
    add_rule(vpath, "CODE", "regex", r"^[A-Z]{3}\d{3}$")
    result = validate_entries({"CODE": "ABC123"}, vpath)
    assert not result.has_errors()


def test_validate_regex_fails(vpath):
    add_rule(vpath, "CODE", "regex", r"^[A-Z]{3}\d{3}$")
    result = validate_entries({"CODE": "abc123"}, vpath)
    assert result.has_errors()


def test_validate_nonempty_fails_for_blank(vpath):
    add_rule(vpath, "TOKEN", "nonempty", "true")
    result = validate_entries({"TOKEN": "   "}, vpath)
    assert result.has_errors()


def test_validate_missing_key_produces_warning(vpath):
    add_rule(vpath, "REQUIRED_KEY", "type", "int")
    result = validate_entries({}, vpath)
    assert result.has_warnings()
    assert not result.has_errors()


def test_validation_result_summary(vpath):
    add_rule(vpath, "PORT", "type", "int")
    add_rule(vpath, "TOKEN", "nonempty", "true")
    result = validate_entries({"PORT": "bad", "TOKEN": ""}, vpath)
    summary = result.summary()
    assert "error" in summary


def test_issue_to_dict():
    issue = ValidationIssue(key="K", rule="type", message="msg", severity="error")
    d = issue.to_dict()
    assert d["key"] == "K"
    assert d["severity"] == "error"
