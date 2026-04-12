"""Lint vault entries for common issues such as empty values,
keys with unusual characters, or duplicate-like keys."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List

from envault.vault import Vault


class LintError(Exception):
    """Raised when linting cannot be performed."""


@dataclass
class LintIssue:
    key: str
    severity: str  # 'warning' | 'error'
    message: str


@dataclass
class LintResult:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(i.severity == "error" for i in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(i.severity == "warning" for i in self.issues)

    def summary(self) -> str:
        errors = sum(1 for i in self.issues if i.severity == "error")
        warnings = sum(1 for i in self.issues if i.severity == "warning")
        return f"{errors} error(s), {warnings} warning(s)"


_VALID_KEY_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


def lint_vault(vault: Vault, password: str) -> LintResult:
    """Inspect all entries in *vault* and return a :class:`LintResult`."""
    result = LintResult()
    entries: Dict[str, str] = vault.list(password)

    seen_upper: Dict[str, str] = {}

    for key, value in entries.items():
        # Error: key does not match conventional env-var naming
        if not _VALID_KEY_RE.match(key):
            result.issues.append(
                LintIssue(key=key, severity="error",
                          message=f"Key '{key}' contains invalid characters.")
            )

        # Warning: empty value
        if value == "":
            result.issues.append(
                LintIssue(key=key, severity="warning",
                          message=f"Key '{key}' has an empty value.")
            )

        # Warning: value looks like an unresolved placeholder
        if re.search(r'\$\{[^}]+\}|<[A-Z_]+>', value):
            result.issues.append(
                LintIssue(key=key, severity="warning",
                          message=f"Key '{key}' value appears to contain an unresolved placeholder.")
            )

        # Warning: duplicate-like keys (case-insensitive collision)
        upper = key.upper()
        if upper in seen_upper:
            result.issues.append(
                LintIssue(key=key, severity="warning",
                          message=(
                              f"Key '{key}' is a case-insensitive duplicate of '{seen_upper[upper]}'."
                          ))
            )
        else:
            seen_upper[upper] = key

    return result
