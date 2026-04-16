"""Schema validation for vault entries."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


class SchemaError(Exception):
    pass


@dataclass
class FieldRule:
    required: bool = False
    pattern: Optional[str] = None
    min_length: int = 0
    max_length: int = 0  # 0 = unlimited

    def to_dict(self) -> dict:
        return {
            "required": self.required,
            "pattern": self.pattern,
            "min_length": self.min_length,
            "max_length": self.max_length,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "FieldRule":
        return cls(
            required=d.get("required", False),
            pattern=d.get("pattern"),
            min_length=d.get("min_length", 0),
            max_length=d.get("max_length", 0),
        )


@dataclass
class SchemaViolation:
    key: str
    message: str


def _schema_path(vault_path: Path) -> Path:
    return vault_path.with_suffix(".schema.json")


def load_schema(vault_path: Path) -> dict[str, FieldRule]:
    p = _schema_path(vault_path)
    if not p.exists():
        return {}
    raw = json.loads(p.read_text())
    return {k: FieldRule.from_dict(v) for k, v in raw.items()}


def save_schema(vault_path: Path, schema: dict[str, FieldRule]) -> None:
    p = _schema_path(vault_path)
    p.write_text(json.dumps({k: v.to_dict() for k, v in schema.items()}, indent=2))


def add_rule(vault_path: Path, key: str, rule: FieldRule) -> None:
    schema = load_schema(vault_path)
    schema[key] = rule
    save_schema(vault_path, schema)


def remove_rule(vault_path: Path, key: str) -> bool:
    schema = load_schema(vault_path)
    if key not in schema:
        return False
    del schema[key]
    save_schema(vault_path, schema)
    return True


def validate(vault_path: Path, entries: dict[str, str]) -> list[SchemaViolation]:
    schema = load_schema(vault_path)
    violations: list[SchemaViolation] = []
    for key, rule in schema.items():
        value = entries.get(key)
        if value is None:
            if rule.required:
                violations.append(SchemaViolation(key, "required key is missing"))
            continue
        if rule.min_length and len(value) < rule.min_length:
            violations.append(SchemaViolation(key, f"value shorter than min_length={rule.min_length}"))
        if rule.max_length and len(value) > rule.max_length:
            violations.append(SchemaViolation(key, f"value longer than max_length={rule.max_length}"))
        if rule.pattern and not re.fullmatch(rule.pattern, value):
            violations.append(SchemaViolation(key, f"value does not match pattern '{rule.pattern}'"))
    return violations
