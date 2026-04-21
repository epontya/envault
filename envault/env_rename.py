"""Rename or bulk-rename keys inside a vault."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from envault.vault import Vault, VaultNotFoundError


class RenameError(Exception):
    """Raised when a rename operation cannot be completed."""


RenameResult = List[Tuple[str, str]]  # list of (old_key, new_key) pairs renamed


def rename_key(
    vault: Vault,
    old_key: str,
    new_key: str,
    *,
    overwrite: bool = False,
) -> None:
    """Rename *old_key* to *new_key* in *vault*.

    Raises
    ------
    RenameError
        If *old_key* does not exist, *new_key* already exists and
        *overwrite* is False, or *old_key* == *new_key*.
    """
    if old_key == new_key:
        raise RenameError(f"Source and destination keys are identical: '{old_key}'")

    value = vault.get(old_key)
    if value is None:
        raise RenameError(f"Key not found in vault: '{old_key}'")

    if not overwrite and vault.get(new_key) is not None:
        raise RenameError(
            f"Destination key already exists: '{new_key}'. "
            "Use overwrite=True to replace it."
        )

    vault.set(new_key, value)
    vault.delete(old_key)


def bulk_rename(
    vault: Vault,
    mapping: Dict[str, str],
    *,
    overwrite: bool = False,
    skip_missing: bool = False,
) -> RenameResult:
    """Rename multiple keys according to *mapping* ``{old: new}``.

    Parameters
    ----------
    vault:
        The target vault.
    mapping:
        Dictionary of ``{old_key: new_key}`` pairs.
    overwrite:
        If True, existing destination keys are silently overwritten.
    skip_missing:
        If True, source keys that do not exist are silently skipped
        instead of raising :class:`RenameError`.

    Returns
    -------
    RenameResult
        List of ``(old_key, new_key)`` tuples that were successfully renamed.
    """
    renamed: RenameResult = []
    for old_key, new_key in mapping.items():
        try:
            rename_key(vault, old_key, new_key, overwrite=overwrite)
            renamed.append((old_key, new_key))
        except RenameError:
            if not skip_missing:
                raise
    return renamed
