"""Sorting utilities for vault entries."""
from __future__ import annotations

from enum import Enum
from typing import Dict, List, Tuple


class SortError(Exception):
    """Raised when a sort operation fails."""


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class SortBy(str, Enum):
    KEY = "key"
    VALUE = "value"
    LENGTH = "length"  # sort by value length


def sort_entries(
    data: Dict[str, str],
    by: SortBy = SortBy.KEY,
    order: SortOrder = SortOrder.ASC,
    case_sensitive: bool = False,
) -> List[Tuple[str, str]]:
    """Return vault entries as a sorted list of (key, value) tuples.

    Args:
        data: Mapping of key -> value from the vault.
        by: The attribute to sort on (key, value, or value length).
        order: Ascending or descending.
        case_sensitive: Whether string comparisons are case-sensitive.

    Returns:
        Sorted list of (key, value) pairs.

    Raises:
        SortError: If *by* is not a recognised SortBy member.
    """
    if by not in SortBy.__members__.values():
        raise SortError(f"Unknown sort field: {by!r}")

    def _key_fn(item: Tuple[str, str]):
        k, v = item
        if by == SortBy.KEY:
            return k if case_sensitive else k.lower()
        if by == SortBy.VALUE:
            return v if case_sensitive else v.lower()
        if by == SortBy.LENGTH:
            return len(v)
        raise SortError(f"Unhandled sort field: {by!r}")

    reverse = order == SortOrder.DESC
    return sorted(data.items(), key=_key_fn, reverse=reverse)


def sorted_keys(
    data: Dict[str, str],
    order: SortOrder = SortOrder.ASC,
    case_sensitive: bool = False,
) -> List[str]:
    """Return only the sorted keys from *data*."""
    pairs = sort_entries(data, by=SortBy.KEY, order=order, case_sensitive=case_sensitive)
    return [k for k, _ in pairs]
