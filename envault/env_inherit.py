"""Inheritance chains for vaults — a child vault inherits keys from a parent."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from envault.vault import Vault, VaultNotFoundError


class InheritError(Exception):
    pass


def _inherit_path(vault_path: Path) -> Path:
    return vault_path.with_suffix(".inherit.json")


def _load(vault_path: Path) -> List[str]:
    p = _inherit_path(vault_path)
    if not p.exists():
        return []
    return json.loads(p.read_text())


def _save(vault_path: Path, parents: List[str]) -> None:
    _inherit_path(vault_path).write_text(json.dumps(parents))


def add_parent(vault_path: Path, parent_path: str) -> List[str]:
    parents = _load(vault_path)
    if parent_path in parents:
        raise InheritError(f"Parent already registered: {parent_path}")
    parents.append(parent_path)
    _save(vault_path, parents)
    return parents


def remove_parent(vault_path: Path, parent_path: str) -> bool:
    parents = _load(vault_path)
    if parent_path not in parents:
        return False
    parents.remove(parent_path)
    _save(vault_path, parents)
    return True


def list_parents(vault_path: Path) -> List[str]:
    return _load(vault_path)


def resolve_inherited(vault_path: Path, password: str) -> Dict[str, str]:
    """Return merged env dict: parents first, child last (child wins)."""
    merged: Dict[str, str] = {}
    for parent_str in _load(vault_path):
        parent_p = Path(parent_str)
        if not parent_p.exists():
            raise InheritError(f"Parent vault not found: {parent_str}")
        try:
            pv = Vault(parent_p, password)
            for key in pv.list():
                val = pv.get(key)
                if val is not None:
                    merged[key] = val
        except Exception as exc:
            raise InheritError(f"Failed to read parent {parent_str}: {exc}") from exc
    child = Vault(vault_path, password)
    for key in child.list():
        val = child.get(key)
        if val is not None:
            merged[key] = val
    return merged
