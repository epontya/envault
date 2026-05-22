"""Patch (partial update) operations for vault entries."""
from __future__ import annotations

from typing import Dict, List, Optional

from envault.vault import Vault, VaultNotFoundError


class PatchError(Exception):
    """Raised when a patch operation fails."""


def apply_patch(
    vault: Vault,
    patch: Dict[str, Optional[str]],
    *,
    add_new: bool = True,
    remove_nulls: bool = True,
) -> Dict[str, str]:
    """Apply a patch dict to a vault.

    Keys with ``None`` values are deleted (when *remove_nulls* is True).
    Keys absent from the vault are added only when *add_new* is True.

    Returns a summary dict with keys ``added``, ``updated``, ``removed``
    each mapping to a list of key names.
    """
    if not isinstance(patch, dict):
        raise PatchError("patch must be a dict")

    added: List[str] = []
    updated: List[str] = []
    removed: List[str] = []

    for key, value in patch.items():
        if not isinstance(key, str) or not key:
            raise PatchError(f"invalid key in patch: {key!r}")

        if value is None:
            if remove_nulls:
                if vault.delete(key):
                    removed.append(key)
            continue

        existing = vault.get(key)
        if existing is None:
            if add_new:
                vault.set(key, value)
                added.append(key)
        else:
            vault.set(key, value)
            updated.append(key)

    return {"added": added, "updated": updated, "removed": removed}


def patch_from_dict(
    vault_path: str,
    password: str,
    patch: Dict[str, Optional[str]],
    *,
    add_new: bool = True,
    remove_nulls: bool = True,
) -> Dict[str, List[str]]:
    """Convenience wrapper that opens a vault by path, applies *patch*, and
    returns the summary produced by :func:`apply_patch`.
    """
    vault = Vault(vault_path, password)
    return apply_patch(vault, patch, add_new=add_new, remove_nulls=remove_nulls)
