"""Archive and unarchive vault entries (soft-delete with recovery)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


class ArchiveError(Exception):
    """Raised on archive operation failures."""


def _archive_path(vault_path: str | Path) -> Path:
    p = Path(vault_path)
    return p.parent / (p.stem + ".archive.json")


def _load(vault_path: str | Path) -> Dict[str, dict]:
    ap = _archive_path(vault_path)
    if not ap.exists():
        return {}
    return json.loads(ap.read_text())


def _save(vault_path: str | Path, data: Dict[str, dict]) -> None:
    _archive_path(vault_path).write_text(json.dumps(data, indent=2))


def archive_key(vault_path: str | Path, key: str, value: str) -> dict:
    """Move a key/value into the archive store."""
    if not key:
        raise ArchiveError("Key must not be empty.")
    data = _load(vault_path)
    entry = {
        "key": key,
        "value": value,
        "archived_at": datetime.now(timezone.utc).isoformat(),
    }
    data[key] = entry
    _save(vault_path, data)
    return entry


def restore_key(vault_path: str | Path, key: str) -> Optional[str]:
    """Remove a key from the archive and return its value, or None if not found."""
    data = _load(vault_path)
    entry = data.pop(key, None)
    if entry is None:
        return None
    _save(vault_path, data)
    return entry["value"]


def list_archived(vault_path: str | Path) -> List[dict]:
    """Return all archived entries sorted by archived_at ascending."""
    data = _load(vault_path)
    return sorted(data.values(), key=lambda e: e["archived_at"])


def purge_key(vault_path: str | Path, key: str) -> bool:
    """Permanently delete an archived key. Returns True if it existed."""
    data = _load(vault_path)
    if key not in data:
        return False
    del data[key]
    _save(vault_path, data)
    return True


def purge_all(vault_path: str | Path) -> int:
    """Permanently delete all archived entries. Returns count removed."""
    data = _load(vault_path)
    count = len(data)
    _save(vault_path, {})
    return count
