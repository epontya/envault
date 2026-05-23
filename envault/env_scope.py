"""Scope management for environment variables — assign keys to named scopes (e.g. dev, staging, prod)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


class ScopeError(Exception):
    """Raised when a scope operation fails."""


def _scope_path(vault_path: str | Path) -> Path:
    p = Path(vault_path)
    return p.parent / f".{p.stem}_scopes.json"


def _load(vault_path: str | Path) -> Dict[str, List[str]]:
    sp = _scope_path(vault_path)
    if not sp.exists():
        return {}
    return json.loads(sp.read_text())


def _save(vault_path: str | Path, data: Dict[str, List[str]]) -> None:
    _scope_path(vault_path).write_text(json.dumps(data, indent=2))


def assign_scope(vault_path: str | Path, key: str, scope: str) -> List[str]:
    """Assign *key* to *scope*. Returns updated list of scopes for that key."""
    if not key:
        raise ScopeError("key must not be empty")
    if not scope:
        raise ScopeError("scope must not be empty")
    data = _load(vault_path)
    scopes = data.get(key, [])
    if scope not in scopes:
        scopes.append(scope)
    data[key] = sorted(scopes)
    _save(vault_path, data)
    return data[key]


def remove_scope(vault_path: str | Path, key: str, scope: str) -> bool:
    """Remove *scope* from *key*. Returns True if it existed."""
    data = _load(vault_path)
    scopes = data.get(key, [])
    if scope not in scopes:
        return False
    scopes.remove(scope)
    if scopes:
        data[key] = scopes
    else:
        data.pop(key, None)
    _save(vault_path, data)
    return True


def get_scopes(vault_path: str | Path, key: str) -> List[str]:
    """Return all scopes assigned to *key*."""
    return _load(vault_path).get(key, [])


def keys_in_scope(vault_path: str | Path, scope: str) -> List[str]:
    """Return all keys that belong to *scope*."""
    data = _load(vault_path)
    return sorted(k for k, scopes in data.items() if scope in scopes)


def list_scopes(vault_path: str | Path) -> List[str]:
    """Return a sorted list of all distinct scopes."""
    data = _load(vault_path)
    all_scopes: set[str] = set()
    for scopes in data.values():
        all_scopes.update(scopes)
    return sorted(all_scopes)
