"""Key/value transformation utilities for vault entries."""
from __future__ import annotations

import re
from typing import Callable, Dict, Optional


class TransformError(Exception):
    """Raised when a transformation cannot be applied."""


# ---------------------------------------------------------------------------
# Built-in transformers
# ---------------------------------------------------------------------------

def _to_upper(value: str) -> str:
    return value.upper()


def _to_lower(value: str) -> str:
    return value.lower()


def _strip_whitespace(value: str) -> str:
    return value.strip()


def _trim_quotes(value: str) -> str:
    """Remove a single surrounding pair of single or double quotes."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return value[1:-1]
    return value


def _mask(value: str) -> str:
    """Replace all characters except the last two with asterisks."""
    if len(value) <= 2:
        return "*" * len(value)
    return "*" * (len(value) - 2) + value[-2:]


_REGISTRY: Dict[str, Callable[[str], str]] = {
    "upper": _to_upper,
    "lower": _to_lower,
    "strip": _strip_whitespace,
    "trim_quotes": _trim_quotes,
    "mask": _mask,
}


def list_transforms() -> list[str]:
    """Return the names of all available built-in transforms."""
    return sorted(_REGISTRY.keys())


def apply_transform(name: str, value: str) -> str:
    """Apply a named transform to *value*.

    Raises
    ------
    TransformError
        If *name* is not a registered transform.
    """
    fn = _REGISTRY.get(name)
    if fn is None:
        available = ", ".join(sorted(_REGISTRY))
        raise TransformError(
            f"Unknown transform '{name}'. Available: {available}"
        )
    return fn(value)


def apply_transforms(names: list[str], value: str) -> str:
    """Apply a pipeline of named transforms to *value* in order."""
    for name in names:
        value = apply_transform(name, value)
    return value


def transform_dict(
    data: Dict[str, str],
    names: list[str],
    key_pattern: Optional[str] = None,
) -> Dict[str, str]:
    """Apply *names* transforms to every value in *data*.

    If *key_pattern* is provided (a glob-style ``*``/``?`` pattern compiled
    via :func:`re.fullmatch`), only matching keys are transformed.
    """
    if key_pattern is not None:
        regex = re.compile(
            re.escape(key_pattern).replace(r"\*", ".*").replace(r"\?", "."),
            re.IGNORECASE,
        )
    else:
        regex = None

    result: Dict[str, str] = {}
    for k, v in data.items():
        if regex is None or regex.fullmatch(k):
            result[k] = apply_transforms(names, v)
        else:
            result[k] = v
    return result
