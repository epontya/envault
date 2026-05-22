"""env_mask.py – mask/unmask sensitive vault values for safe display."""
from __future__ import annotations

import re
from typing import Dict, List, Optional

_SENSITIVE_PATTERNS: List[str] = [
    r"pass(word)?",
    r"secret",
    r"token",
    r"api[_-]?key",
    r"auth",
    r"credential",
    r"private[_-]?key",
    r"access[_-]?key",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _SENSITIVE_PATTERNS]

DEFAULT_MASK = "********"


class MaskError(Exception):
    """Raised when masking operations fail."""


def is_sensitive_key(key: str, extra_patterns: Optional[List[str]] = None) -> bool:
    """Return True if *key* looks like it holds a sensitive value."""
    patterns = _COMPILED[:]
    if extra_patterns:
        patterns += [re.compile(p, re.IGNORECASE) for p in extra_patterns]
    return any(p.search(key) for p in patterns)


def mask_value(
    value: str,
    *,
    mask: str = DEFAULT_MASK,
    reveal_chars: int = 0,
) -> str:
    """Return a masked representation of *value*.

    If *reveal_chars* > 0, the last N characters are kept visible.
    """
    if not isinstance(value, str):
        raise MaskError(f"Expected str, got {type(value).__name__}")
    if reveal_chars < 0:
        raise MaskError("reveal_chars must be >= 0")
    if reveal_chars == 0 or reveal_chars >= len(value):
        return mask
    return mask + value[-reveal_chars:]


def mask_dict(
    data: Dict[str, str],
    *,
    mask: str = DEFAULT_MASK,
    reveal_chars: int = 0,
    extra_patterns: Optional[List[str]] = None,
) -> Dict[str, str]:
    """Return a copy of *data* with sensitive values masked."""
    result: Dict[str, str] = {}
    for key, value in data.items():
        if is_sensitive_key(key, extra_patterns):
            result[key] = mask_value(value, mask=mask, reveal_chars=reveal_chars)
        else:
            result[key] = value
    return result
