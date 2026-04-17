"""Per-field encryption metadata for vault entries."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List


class FieldEncryptError(Exception):
    pass


def _field_meta_path(vault_path: str | Path) -> Path:
    p = Path(vault_path)
    return p.parent / (p.stem + ".fieldmeta.json")


def _load(vault_path: str | Path) -> dict:
    path = _field_meta_path(vault_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save(vault_path: str | Path, data: dict) -> None:
    path = _field_meta_path(vault_path)
    path.write_text(json.dumps(data, indent=2))


def mark_sensitive(vault_path: str | Path, key: str) -> None:
    """Mark a key as sensitive (double-encrypted / masked in output)."""
    data = _load(vault_path)
    entry = data.get(key, {})
    entry["sensitive"] = True
    data[key] = entry
    _save(vault_path, data)


def unmark_sensitive(vault_path: str | Path, key: str) -> bool:
    """Remove sensitive mark from a key. Returns True if it existed."""
    data = _load(vault_path)
    if key not in data:
        return False
    data[key].pop("sensitive", None)
    if not data[key]:
        del data[key]
    _save(vault_path, data)
    return True


def is_sensitive(vault_path: str | Path, key: str) -> bool:
    data = _load(vault_path)
    return bool(data.get(key, {}).get("sensitive", False))


def list_sensitive(vault_path: str | Path) -> List[str]:
    data = _load(vault_path)
    return sorted(k for k, v in data.items() if v.get("sensitive"))
