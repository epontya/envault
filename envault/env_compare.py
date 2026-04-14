"""Compare vault contents against a live .env file or environment."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envault.vault import Vault


class CompareError(Exception):
    """Raised when a comparison operation fails."""


@dataclass
class CompareResult:
    only_in_vault: List[str] = field(default_factory=list)
    only_in_source: List[str] = field(default_factory=list)
    value_differs: List[str] = field(default_factory=list)
    matching: List[str] = field(default_factory=list)

    def has_differences(self) -> bool:
        return bool(self.only_in_vault or self.only_in_source or self.value_differs)

    def summary(self) -> str:
        lines = []
        for k in sorted(self.only_in_vault):
            lines.append(f"  only-in-vault  : {k}")
        for k in sorted(self.only_in_source):
            lines.append(f"  only-in-source : {k}")
        for k in sorted(self.value_differs):
            lines.append(f"  value-differs  : {k}")
        for k in sorted(self.matching):
            lines.append(f"  match          : {k}")
        return "\n".join(lines) if lines else "  (no entries)"


def _parse_dotenv(path: Path) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            result[key] = value
    return result


def compare_with_dotenv(
    vault: Vault,
    dotenv_path: Path,
    keys: Optional[List[str]] = None,
) -> CompareResult:
    """Compare vault entries against a .env file."""
    if not dotenv_path.exists():
        raise CompareError(f".env file not found: {dotenv_path}")
    source = _parse_dotenv(dotenv_path)
    return _compare(vault, source, keys)


def compare_with_env(
    vault: Vault,
    keys: Optional[List[str]] = None,
) -> CompareResult:
    """Compare vault entries against the current process environment."""
    source = dict(os.environ)
    return _compare(vault, source, keys)


def _compare(
    vault: Vault,
    source: Dict[str, str],
    keys: Optional[List[str]],
) -> CompareResult:
    vault_data: Dict[str, str] = {}
    for k in vault.list():
        val = vault.get(k)
        if val is not None:
            vault_data[k] = val

    candidates = set(keys) if keys else set(vault_data) | set(source)
    result = CompareResult()

    for k in candidates:
        in_vault = k in vault_data
        in_source = k in source
        if in_vault and in_source:
            if vault_data[k] == source[k]:
                result.matching.append(k)
            else:
                result.value_differs.append(k)
        elif in_vault:
            result.only_in_vault.append(k)
        elif in_source:
            result.only_in_source.append(k)

    return result
