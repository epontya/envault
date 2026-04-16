"""Tests for envault.env_schema."""
from __future__ import annotations

from pathlib import Path

import pytest

from envault.env_schema import (
    FieldRule,
    SchemaViolation,
    add_rule,
    load_schema,
    remove_rule,
    validate,
)


@pytest.fixture
def vpath(tmp_path) -> Path:
    return tmp_path / "vault.db"


def test_load_schema_missing_file_returns_empty(vpath):
    assert load_schema(vpath) == {}


def test_add_rule_creates_schema_file(vpath):
    add_rule(vpath, "API_KEY", FieldRule(required=True))
    schema_file = vpath.with_suffix(".schema.json")
    assert schema_file.exists()


def test_add_and_load_rule(vpath):
    add_rule(vpath, "API_KEY", FieldRule(required=True, min_length=8))
    schema = load_schema(vpath)
    assert "API_KEY" in schema
    assert schema["API_KEY"].required is True
    assert schema["API_KEY"].min_length == 8


def test_remove_existing_rule(vpath):
    add_rule(vpath, "TOKEN", FieldRule(required=True))
    result = remove_rule(vpath, "TOKEN")
    assert result is True
    assert "TOKEN" not in load_schema(vpath)


def test_remove_missing_rule_returns_false(vpath):
    assert remove_rule(vpath, "NONEXISTENT") is False


def test_validate_no_violations_for_clean_entries(vpath):
    add_rule(vpath, "DB_URL", FieldRule(required=True, min_length=3))
    violations = validate(vpath, {"DB_URL": "postgres://localhost"})
    assert violations == []


def test_validate_required_missing(vpath):
    add_rule(vpath, "SECRET", FieldRule(required=True))
    violations = validate(vpath, {})
    assert len(violations) == 1
    assert violations[0].key == "SECRET"
    assert "required" in violations[0].message


def test_validate_min_length_violation(vpath):
    add_rule(vpath, "TOKEN", FieldRule(min_length=10))
    violations = validate(vpath, {"TOKEN": "short"})
    assert any("min_length" in v.message for v in violations)


def test_validate_max_length_violation(vpath):
    add_rule(vpath, "CODE", FieldRule(max_length=5))
    violations = validate(vpath, {"CODE": "toolongvalue"})
    assert any("max_length" in v.message for v in violations)


def test_validate_pattern_violation(vpath):
    add_rule(vpath, "PORT", FieldRule(pattern=r"\d+"))
    violations = validate(vpath, {"PORT": "not-a-number"})
    assert any("pattern" in v.message for v in violations)


def test_validate_pattern_match_no_violation(vpath):
    add_rule(vpath, "PORT", FieldRule(pattern=r"\d+"))
    violations = validate(vpath, {"PORT": "8080"})
    assert violations == []


def test_field_rule_round_trip():
    rule = FieldRule(required=True, pattern=r"[A-Z]+", min_length=2, max_length=20)
    restored = FieldRule.from_dict(rule.to_dict())
    assert restored.required == rule.required
    assert restored.pattern == rule.pattern
    assert restored.min_length == rule.min_length
    assert restored.max_length == rule.max_length
