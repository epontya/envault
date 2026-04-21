"""Filter vault entries by key pattern, value pattern, or tag."""
from __future__ import annotations

import fnmatch
import re
from typing import Dict, List, Optional

from envault.vault import Vault


class FilterError(Exception):
    """Raised when a filter operation fails."""


def filter_by_key(
    data: Dict[str, str],
    pattern: str,
    *,
    case_sensitive: bool = False,
) -> Dict[str, str]:
    """Return entries whose keys match a glob *pattern*."""
    if not pattern:
        raise FilterError("pattern must not be empty")
    flags = 0 if case_sensitive else re.IGNORECASE
    # Convert glob to regex so we can respect case_sensitive uniformly.
    regex = fnmatch.translate(pattern)
    compiled = re.compile(regex, flags)
    return {k: v for k, v in data.items() if compiled.match(k)}


def filter_by_value(
    data: Dict[str, str],
    substring: str,
    *,
    case_sensitive: bool = False,
) -> Dict[str, str]:
    """Return entries whose values contain *substring*."""
    if not case_sensitive:
        substring = substring.lower()
        return {k: v for k, v in data.items() if substring in v.lower()}
    return {k: v for k, v in data.items() if substring in v}


def filter_by_prefix(data: Dict[str, str], prefix: str) -> Dict[str, str]:
    """Return entries whose keys start with *prefix* (case-sensitive)."""
    if not prefix:
        raise FilterError("prefix must not be empty")
    return {k: v for k, v in data.items() if k.startswith(prefix)}


def filter_keys(
    vault_path: str,
    password: str,
    *,
    key_pattern: Optional[str] = None,
    value_substring: Optional[str] = None,
    prefix: Optional[str] = None,
    case_sensitive: bool = False,
) -> Dict[str, str]:
    """Load *vault_path* and apply one or more filters, returning matching entries.

    Filters are applied in order: key_pattern → prefix → value_substring.
    All supplied filters must match (AND semantics).
    """
    vault = Vault(vault_path, password)
    data: Dict[str, str] = {}
    for key in vault.list():
        value = vault.get(key)
        if value is not None:
            data[key] = value

    if key_pattern is not None:
        data = filter_by_key(data, key_pattern, case_sensitive=case_sensitive)
    if prefix is not None:
        data = filter_by_prefix(data, prefix)
    if value_substring is not None:
        data = filter_by_value(data, value_substring, case_sensitive=case_sensitive)
    return data
