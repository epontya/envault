"""Redaction utilities for masking sensitive vault values in output."""

from __future__ import annotations

import re
from typing import Dict, List, Optional

DEFAULT_MASK = "****"
DEFAULT_SENSITIVE_PATTERNS = [
    re.compile(r"(password|passwd|secret|token|key|api_?key|auth|credential)", re.IGNORECASE),
]


class RedactError(Exception):
    """Raised when redaction configuration is invalid."""


def is_sensitive_key(key: str, patterns: Optional[List[re.Pattern]] = None) -> bool:
    """Return True if *key* matches any sensitive pattern."""
    if patterns is None:
        patterns = DEFAULT_SENSITIVE_PATTERNS
    return any(p.search(key) for p in patterns)


def redact_value(value: str, visible_chars: int = 0, mask: str = DEFAULT_MASK) -> str:
    """Return a redacted version of *value*.

    If *visible_chars* > 0, that many trailing characters are preserved.
    """
    if visible_chars < 0:
        raise RedactError("visible_chars must be >= 0")
    if not value:
        return mask
    if visible_chars == 0 or visible_chars >= len(value):
        return mask
    return mask + value[-visible_chars:]


def redact_dict(
    data: Dict[str, str],
    *,
    patterns: Optional[List[re.Pattern]] = None,
    visible_chars: int = 0,
    mask: str = DEFAULT_MASK,
    keys: Optional[List[str]] = None,
) -> Dict[str, str]:
    """Return a copy of *data* with sensitive values redacted.

    If *keys* is provided, only those keys are redacted regardless of patterns.
    Otherwise, keys matching *patterns* are redacted.
    """
    result: Dict[str, str] = {}
    for k, v in data.items():
        should_redact = (keys is not None and k in keys) or (
            keys is None and is_sensitive_key(k, patterns)
        )
        result[k] = redact_value(v, visible_chars=visible_chars, mask=mask) if should_redact else v
    return result
