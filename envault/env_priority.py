"""Priority assignment for vault keys."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

PRIORITY_LEVELS = ("low", "normal", "high", "critical")


class PriorityError(Exception):
    """Raised when a priority operation fails."""


def _priority_path(vault_path: str | Path) -> Path:
    p = Path(vault_path)
    return p.parent / f".{p.stem}_priority.json"


def _load(vault_path: str | Path) -> Dict[str, str]:
    path = _priority_path(vault_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save(vault_path: str | Path, data: Dict[str, str]) -> None:
    _priority_path(vault_path).write_text(json.dumps(data, indent=2))


def set_priority(vault_path: str | Path, key: str, level: str) -> str:
    """Assign a priority level to a key. Returns the level."""
    if not key:
        raise PriorityError("Key must not be empty.")
    if level not in PRIORITY_LEVELS:
        raise PriorityError(
            f"Invalid priority '{level}'. Choose from: {', '.join(PRIORITY_LEVELS)}"
        )
    data = _load(vault_path)
    data[key] = level
    _save(vault_path, data)
    return level


def get_priority(vault_path: str | Path, key: str) -> Optional[str]:
    """Return the priority level for a key, or None if not set."""
    return _load(vault_path).get(key)


def remove_priority(vault_path: str | Path, key: str) -> bool:
    """Remove priority for a key. Returns True if it existed."""
    data = _load(vault_path)
    if key not in data:
        return False
    del data[key]
    _save(vault_path, data)
    return True


def list_by_priority(
    vault_path: str | Path, level: Optional[str] = None
) -> Dict[str, str]:
    """Return all key→level mappings, optionally filtered by level."""
    data = _load(vault_path)
    if level is None:
        return dict(data)
    if level not in PRIORITY_LEVELS:
        raise PriorityError(
            f"Invalid priority '{level}'. Choose from: {', '.join(PRIORITY_LEVELS)}"
        )
    return {k: v for k, v in data.items() if v == level}
