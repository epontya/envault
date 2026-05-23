"""env_format.py – value formatting utilities for vault entries."""
from __future__ import annotations

import re
from typing import Dict, Optional


class FormatError(Exception):
    """Raised when a formatting operation fails."""


_BOOL_TRUE = {"true", "1", "yes", "on"}
_BOOL_FALSE = {"false", "0", "no", "off"}


def format_as_bool(value: str) -> str:
    """Normalise a boolean-like string to 'true' or 'false'."""
    normalised = value.strip().lower()
    if normalised in _BOOL_TRUE:
        return "true"
    if normalised in _BOOL_FALSE:
        return "false"
    raise FormatError(f"Cannot interpret {value!r} as a boolean.")


def format_as_int(value: str) -> str:
    """Ensure the value is a valid integer string."""
    stripped = value.strip()
    try:
        return str(int(stripped))
    except ValueError:
        raise FormatError(f"Cannot interpret {value!r} as an integer.")


def format_as_float(value: str) -> str:
    """Ensure the value is a valid float string."""
    stripped = value.strip()
    try:
        return str(float(stripped))
    except ValueError:
        raise FormatError(f"Cannot interpret {value!r} as a float.")


def format_as_url(value: str) -> str:
    """Validate and normalise a URL value (lowercase scheme + host)."""
    stripped = value.strip()
    pattern = re.compile(r"^(https?|ftp)://", re.IGNORECASE)
    if not pattern.match(stripped):
        raise FormatError(f"{value!r} does not look like a URL.")
    scheme_end = stripped.index("://") + 3
    scheme = stripped[:scheme_end].lower()
    rest = stripped[scheme_end:]
    slash = rest.find("/")
    if slash == -1:
        host = rest.lower()
        path = ""
    else:
        host = rest[:slash].lower()
        path = rest[slash:]
    return scheme + host + path


_FORMATTERS: Dict[str, object] = {
    "bool": format_as_bool,
    "int": format_as_int,
    "float": format_as_float,
    "url": format_as_url,
}


def list_formats() -> list[str]:
    """Return sorted list of available format names."""
    return sorted(_FORMATTERS.keys())


def apply_format(value: str, fmt: str) -> str:
    """Apply a named format to *value*.

    Raises FormatError for unknown format names or invalid values.
    """
    key = fmt.strip().lower()
    fn = _FORMATTERS.get(key)
    if fn is None:
        raise FormatError(
            f"Unknown format {fmt!r}. Available: {list_formats()}"
        )
    return fn(value)  # type: ignore[operator]
