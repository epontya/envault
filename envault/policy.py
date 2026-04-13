"""Password policy enforcement for vault secrets."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional


class PolicyError(Exception):
    """Raised when a policy operation fails."""


@dataclass
class PolicyConfig:
    min_length: int = 8
    require_uppercase: bool = False
    require_lowercase: bool = False
    require_digit: bool = False
    require_special: bool = False
    max_length: Optional[int] = None
    forbidden_patterns: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "PolicyConfig":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class PolicyViolation:
    rule: str
    message: str


def _policy_path(vault_path: Path) -> Path:
    return vault_path.parent / (vault_path.stem + ".policy.json")


def load_policy(vault_path: Path) -> PolicyConfig:
    p = _policy_path(vault_path)
    if not p.exists():
        return PolicyConfig()
    return PolicyConfig.from_dict(json.loads(p.read_text()))


def save_policy(vault_path: Path, config: PolicyConfig) -> None:
    p = _policy_path(vault_path)
    p.write_text(json.dumps(config.to_dict(), indent=2))


def check_value(value: str, config: PolicyConfig) -> List[PolicyViolation]:
    """Return a list of policy violations for *value*."""
    violations: List[PolicyViolation] = []

    if len(value) < config.min_length:
        violations.append(PolicyViolation("min_length", f"Value must be at least {config.min_length} characters."))

    if config.max_length is not None and len(value) > config.max_length:
        violations.append(PolicyViolation("max_length", f"Value must be at most {config.max_length} characters."))

    if config.require_uppercase and not any(c.isupper() for c in value):
        violations.append(PolicyViolation("require_uppercase", "Value must contain at least one uppercase letter."))

    if config.require_lowercase and not any(c.islower() for c in value):
        violations.append(PolicyViolation("require_lowercase", "Value must contain at least one lowercase letter."))

    if config.require_digit and not any(c.isdigit() for c in value):
        violations.append(PolicyViolation("require_digit", "Value must contain at least one digit."))

    if config.require_special and not re.search(r'[^A-Za-z0-9]', value):
        violations.append(PolicyViolation("require_special", "Value must contain at least one special character."))

    for pattern in config.forbidden_patterns:
        if re.search(pattern, value):
            violations.append(PolicyViolation("forbidden_pattern", f"Value matches forbidden pattern: {pattern}"))

    return violations
