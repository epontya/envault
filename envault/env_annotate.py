"""env_annotate.py – attach arbitrary metadata annotations to vault keys."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class AnnotateError(Exception):
    """Raised when an annotation operation fails."""


def _annotate_path(vault_path: str | Path) -> Path:
    p = Path(vault_path)
    return p.parent / (p.stem + ".annotations.json")


def _load(vault_path: str | Path) -> dict[str, dict[str, Any]]:
    ap = _annotate_path(vault_path)
    if not ap.exists():
        return {}
    return json.loads(ap.read_text())


def _save(vault_path: str | Path, data: dict[str, dict[str, Any]]) -> None:
    _annotate_path(vault_path).write_text(json.dumps(data, indent=2))


def set_annotation(vault_path: str | Path, key: str, field: str, value: Any) -> dict[str, Any]:
    """Set a metadata *field* on *key*. Returns the updated annotation dict for the key."""
    if not key:
        raise AnnotateError("key must not be empty")
    if not field:
        raise AnnotateError("field must not be empty")
    data = _load(vault_path)
    data.setdefault(key, {})[field] = value
    _save(vault_path, data)
    return dict(data[key])


def get_annotation(vault_path: str | Path, key: str, field: str | None = None) -> Any:
    """Return annotation(s) for *key*. If *field* is given, return that field's value."""
    data = _load(vault_path)
    entry = data.get(key, {})
    if field is None:
        return dict(entry)
    return entry.get(field)


def remove_annotation(vault_path: str | Path, key: str, field: str) -> bool:
    """Remove a single annotation field from *key*. Returns True if it existed."""
    data = _load(vault_path)
    entry = data.get(key, {})
    if field not in entry:
        return False
    del entry[field]
    if not entry:
        data.pop(key, None)
    else:
        data[key] = entry
    _save(vault_path, data)
    return True


def list_annotations(vault_path: str | Path) -> dict[str, dict[str, Any]]:
    """Return all annotations for every key in the vault."""
    return _load(vault_path)
