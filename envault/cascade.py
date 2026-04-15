"""Cascade: merge multiple vault profiles into a resolved key-value mapping.

Later profiles in the list take precedence over earlier ones (higher priority).
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from envault.vault import Vault, VaultNotFoundError


class CascadeError(Exception):
    """Raised when cascade resolution fails."""


def _load_vault_data(vault_path: str, password: str) -> Dict[str, str]:
    """Load all key-value pairs from a single vault file."""
    try:
        v = Vault(vault_path, password)
        return v.all()
    except VaultNotFoundError as exc:
        raise CascadeError(f"Vault not found: {vault_path}") from exc
    except ValueError as exc:
        raise CascadeError(f"Cannot decrypt vault '{vault_path}': {exc}") from exc


def resolve(
    vault_paths: List[str],
    password: str,
    keys: Optional[List[str]] = None,
) -> Dict[str, str]:
    """Merge vaults left-to-right; rightmost value wins for duplicate keys.

    Args:
        vault_paths: Ordered list of vault file paths (lowest to highest priority).
        password:    Shared decryption password used for every vault.
        keys:        Optional allowlist of keys to include in the result.

    Returns:
        A flat dict of resolved key-value pairs.
    """
    if not vault_paths:
        raise CascadeError("At least one vault path is required.")

    merged: Dict[str, str] = {}
    for path in vault_paths:
        data = _load_vault_data(path, password)
        merged.update(data)

    if keys is not None:
        merged = {k: v for k, v in merged.items() if k in keys}

    return merged


def resolve_with_origins(
    vault_paths: List[str],
    password: str,
) -> Dict[str, Tuple[str, str]]:
    """Like resolve(), but also records which vault each key came from.

    Returns:
        A dict mapping key -> (value, source_vault_path).
    """
    if not vault_paths:
        raise CascadeError("At least one vault path is required.")

    result: Dict[str, Tuple[str, str]] = {}
    for path in vault_paths:
        data = _load_vault_data(path, password)
        for k, v in data.items():
            result[k] = (v, path)

    return result
