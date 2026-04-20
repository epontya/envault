"""Runtime validation of vault entries against expected types and patterns."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class ValidationError(Exception):
    """Raised when a validation rule cannot be applied."""


@dataclass
class ValidationIssue:
    key: str
    rule: str
    message: str
    severity: str = "error"  # "error" | "warning"

    def to_dict(self) -> dict:
        return {"key": self.key, "rule": self.rule, "message": self.message, "severity": self.severity}


@dataclass
class ValidationResult:
    issues: list[ValidationIssue] = field(default_factory=list)

    def has_errors(self) -> bool:
        return any(i.severity == "error" for i in self.issues)

    def has_warnings(self) -> bool:
        return any(i.severity == "warning" for i in self.issues)

    def summary(self) -> str:
        errors = sum(1 for i in self.issues if i.severity == "error")
        warnings = sum(1 for i in self.issues if i.severity == "warning")
        return f"{errors} error(s), {warnings} warning(s)"


def _rules_path(vault_path: Path) -> Path:
    return vault_path.with_suffix(".validate.json")


def load_rules(vault_path: Path) -> dict[str, Any]:
    p = _rules_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_rules(vault_path: Path, rules: dict[str, Any]) -> None:
    _rules_path(vault_path).write_text(json.dumps(rules, indent=2))


def add_rule(vault_path: Path, key: str, rule_type: str, rule_value: str) -> None:
    """Add or update a validation rule for *key*.""""
    valid_types = {"type", "regex", "nonempty"}
    if rule_type not in valid_types:
        raise ValidationError(f"Unknown rule type '{rule_type}'. Valid: {sorted(valid_types)}")
    rules = load_rules(vault_path)
    rules.setdefault(key, {})[rule_type] = rule_value
    save_rules(vault_path, rules)


def remove_rule(vault_path: Path, key: str) -> bool:
    rules = load_rules(vault_path)
    if key not in rules:
        return False
    del rules[key]
    save_rules(vault_path, rules)
    return True


def validate_entries(entries: dict[str, str], vault_path: Path) -> ValidationResult:
    """Validate *entries* against stored rules for *vault_path*."""
    rules = load_rules(vault_path)
    result = ValidationResult()
    for key, key_rules in rules.items():
        value = entries.get(key)
        if value is None:
            result.issues.append(ValidationIssue(key, "missing", f"Key '{key}' has rules but is absent from vault.", "warning"))
            continue
        if "nonempty" in key_rules and key_rules["nonempty"] in (True, "true", "1") and not value.strip():
            result.issues.append(ValidationIssue(key, "nonempty", f"'{key}' must not be empty."))
        if "type" in key_rules:
            expected = key_rules["type"]
            if expected == "int":
                try:
                    int(value)
                except ValueError:
                    result.issues.append(ValidationIssue(key, "type", f"'{key}' must be an integer, got '{value}'."))
            elif expected == "float":
                try:
                    float(value)
                except ValueError:
                    result.issues.append(ValidationIssue(key, "type", f"'{key}' must be a float, got '{value}'."))
            elif expected == "bool":
                if value.lower() not in ("true", "false", "1", "0", "yes", "no"):
                    result.issues.append(ValidationIssue(key, "type", f"'{key}' must be a boolean, got '{value}'."))
        if "regex" in key_rules:
            pattern = key_rules["regex"]
            if not re.fullmatch(pattern, value):
                result.issues.append(ValidationIssue(key, "regex", f"'{key}' does not match pattern '{pattern}'."))
    return result
