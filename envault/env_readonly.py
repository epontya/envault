"""Read-only key protection for vault entries."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List


class ReadOnlyError(Exception):
    """Raised when a read-only operation is violated."""


def _readonly_path(vault_path: str) -> Path:
    p = Path(vault_path)
    return p.parent / f".{p.stem}.readonly.json"


def _load(vault_path: str) -> List[str]:
    rp = _readonly_path(vault_path)
    if not rp.exists():
        return []
    return json.loads(rp.read_text())


def _save(vault_path: str, keys: List[str]) -> None:
    _readonly_path(vault_path).write_text(json.dumps(sorted(set(keys)), indent=2))


def protect(vault_path: str, key: str) -> List[str]:
    """Mark *key* as read-only. Returns updated list of protected keys."""
    if not key:
        raise ReadOnlyError("Key must not be empty.")
    keys = _load(vault_path)
    if key not in keys:
        keys.append(key)
    _save(vault_path, keys)
    return sorted(set(keys))


def unprotect(vault_path: str, key: str) -> bool:
    """Remove read-only protection from *key*. Returns True if it existed."""
    keys = _load(vault_path)
    if key not in keys:
        return False
    keys.remove(key)
    _save(vault_path, keys)
    return True


def is_protected(vault_path: str, key: str) -> bool:
    """Return True if *key* is read-only protected."""
    return key in _load(vault_path)


def list_protected(vault_path: str) -> List[str]:
    """Return all currently protected keys, sorted."""
    return sorted(_load(vault_path))


def assert_writable(vault_path: str, key: str) -> None:
    """Raise ReadOnlyError if *key* is protected."""
    if is_protected(vault_path, key):
        raise ReadOnlyError(f"Key '{key}' is read-only and cannot be modified.")
