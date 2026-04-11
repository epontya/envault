"""Search and filter vault entries by key pattern or value content."""

from __future__ import annotations

import fnmatch
import re
from typing import Dict, Optional

from envault.vault import Vault, VaultNotFoundError


class SearchError(Exception):
    """Raised when a search operation fails."""


def search_keys(
    vault: Vault,
    pattern: str,
    *,
    case_sensitive: bool = False,
) -> Dict[str, str]:
    """Return entries whose keys match a glob-style *pattern*.

    Args:
        vault: An open :class:`~envault.vault.Vault` instance.
        pattern: Glob pattern (e.g. ``"DB_*"``, ``"*SECRET*"``).
        case_sensitive: When *False* (default) matching ignores case.

    Returns:
        Mapping of matching key → plaintext value.
    """
    all_keys = vault.list_keys()
    results: Dict[str, str] = {}

    for key in all_keys:
        haystack = key if case_sensitive else key.upper()
        needle = pattern if case_sensitive else pattern.upper()
        if fnmatch.fnmatchcase(haystack, needle):
            value = vault.get(key)
            if value is not None:
                results[key] = value

    return results


def search_values(
    vault: Vault,
    substring: str,
    *,
    case_sensitive: bool = False,
    regex: bool = False,
) -> Dict[str, str]:
    """Return entries whose *values* contain *substring* (or match a regex).

    Args:
        vault: An open :class:`~envault.vault.Vault` instance.
        substring: Plain substring or regex pattern to search for.
        case_sensitive: When *False* (default) matching ignores case.
        regex: Treat *substring* as a regular expression.

    Returns:
        Mapping of matching key → plaintext value.

    Raises:
        SearchError: If *regex* is *True* and the pattern is invalid.
    """
    flags = 0 if case_sensitive else re.IGNORECASE

    if regex:
        try:
            compiled = re.compile(substring, flags)
        except re.error as exc:
            raise SearchError(f"Invalid regex pattern: {exc}") from exc
        match_fn = lambda v: bool(compiled.search(v))  # noqa: E731
    else:
        needle = substring if case_sensitive else substring.lower()
        match_fn = lambda v: needle in (v if case_sensitive else v.lower())  # noqa: E731

    results: Dict[str, str] = {}
    for key in vault.list_keys():
        value = vault.get(key)
        if value is not None and match_fn(value):
            results[key] = value

    return results
