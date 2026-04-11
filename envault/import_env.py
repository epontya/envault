"""Import environment variables from external sources into a vault."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Optional


class ImportError(Exception):  # noqa: A001
    """Raised when an import operation fails."""


def _parse_dotenv_line(line: str) -> Optional[tuple[str, str]]:
    """Parse a single .env line into a (key, value) pair, or None to skip."""
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    if "=" not in line:
        return None
    key, _, raw_value = line.partition("=")
    key = key.strip()
    value = raw_value.strip()
    # Strip surrounding quotes (single or double)
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        value = value[1:-1]
    return key, value


def import_from_dotenv(path: Path) -> Dict[str, str]:
    """Read a .env file and return a dict of key-value pairs."""
    if not path.exists():
        raise ImportError(f"File not found: {path}")
    result: Dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        parsed = _parse_dotenv_line(line)
        if parsed is not None:
            result[parsed[0]] = parsed[1]
    return result


def import_from_json(path: Path) -> Dict[str, str]:
    """Read a JSON file containing a flat string mapping and return it."""
    if not path.exists():
        raise ImportError(f"File not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ImportError(f"Invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ImportError("JSON root must be an object")
    result: Dict[str, str] = {}
    for k, v in data.items():
        if not isinstance(k, str):
            raise ImportError(f"Non-string key encountered: {k!r}")
        result[k] = str(v)
    return result


def import_from_env(prefix: str = "") -> Dict[str, str]:
    """Capture current process environment variables, optionally filtered by prefix."""
    return {
        k: v
        for k, v in os.environ.items()
        if k.startswith(prefix)
    }
