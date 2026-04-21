"""env_chain.py – ordered key-lookup chain across multiple vaults.

A ChainStore resolves keys by searching vaults in priority order
(first vault wins).  The chain configuration is persisted as JSON
next to the primary vault file.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


class ChainError(Exception):
    """Raised for invalid chain operations."""


def _chain_path(vault_path: Path) -> Path:
    return vault_path.with_suffix(".chain.json")


def _load(vault_path: Path) -> List[str]:
    p = _chain_path(vault_path)
    if not p.exists():
        return []
    return json.loads(p.read_text())


def _save(vault_path: Path, chain: List[str]) -> None:
    _chain_path(vault_path).write_text(json.dumps(chain, indent=2))


def add_vault(vault_path: Path, linked: Path) -> List[str]:
    """Append *linked* to the lookup chain of *vault_path*."""
    linked_str = str(linked)
    chain = _load(vault_path)
    if linked_str in chain:
        raise ChainError(f"{linked} is already in the chain")
    chain.append(linked_str)
    _save(vault_path, chain)
    return chain


def remove_vault(vault_path: Path, linked: Path) -> bool:
    """Remove *linked* from the chain; returns True if it was present."""
    linked_str = str(linked)
    chain = _load(vault_path)
    if linked_str not in chain:
        return False
    chain.remove(linked_str)
    _save(vault_path, chain)
    return True


def list_chain(vault_path: Path) -> List[str]:
    """Return the ordered list of linked vault paths."""
    return _load(vault_path)


def resolve_key(vault_path: Path, key: str, password: str) -> Optional[str]:
    """Resolve *key* by searching *vault_path* first, then its chain."""
    from envault.vault import Vault, VaultNotFoundError

    vaults_to_search = [str(vault_path)] + _load(vault_path)
    for vp in vaults_to_search:
        try:
            v = Vault(Path(vp), password)
            value = v.get(key)
            if value is not None:
                return value
        except (VaultNotFoundError, Exception):
            continue
    return None


def resolve_all(vault_path: Path, password: str) -> Dict[str, str]:
    """Merge all vaults in chain order; earlier vaults win on conflict."""
    from envault.vault import Vault, VaultNotFoundError

    merged: Dict[str, str] = {}
    vaults_to_search = [str(vault_path)] + _load(vault_path)
    # Reverse so that earlier vaults overwrite later ones
    for vp in reversed(vaults_to_search):
        try:
            v = Vault(Path(vp), password)
            merged.update(v.all())
        except (VaultNotFoundError, Exception):
            continue
    return merged
