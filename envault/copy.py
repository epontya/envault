"""Copy or move entries between vault profiles or files."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from envault.vault import Vault, VaultNotFoundError


class CopyError(Exception):
    """Raised when a copy/move operation fails."""


def copy_entries(
    src_path: Path,
    src_password: str,
    dst_path: Path,
    dst_password: str,
    keys: Optional[List[str]] = None,
    overwrite: bool = False,
) -> int:
    """Copy entries from *src* vault to *dst* vault.

    Parameters
    ----------
    keys:
        Specific keys to copy.  ``None`` means copy all keys.
    overwrite:
        When *False* (default) existing keys in *dst* are skipped.

    Returns
    -------
    int
        Number of entries actually written.
    """
    if not src_path.exists():
        raise VaultNotFoundError(f"Source vault not found: {src_path}")

    src = Vault(src_path, src_password)
    dst = Vault(dst_path, dst_password)

    all_keys: List[str] = keys if keys is not None else src.keys()

    if not all_keys:
        return 0

    written = 0
    for key in all_keys:
        value = src.get(key)
        if value is None:
            raise CopyError(f"Key '{key}' not found in source vault.")
        if not overwrite and dst.get(key) is not None:
            continue
        dst.set(key, value)
        written += 1

    return written


def move_entries(
    src_path: Path,
    src_password: str,
    dst_path: Path,
    dst_password: str,
    keys: Optional[List[str]] = None,
    overwrite: bool = False,
) -> int:
    """Copy entries then delete them from the source vault.

    Returns the number of entries moved.
    """
    src = Vault(src_path, src_password)
    all_keys: List[str] = keys if keys is not None else src.keys()

    written = copy_entries(
        src_path, src_password, dst_path, dst_password, all_keys, overwrite
    )

    # Only remove keys that were actually written to dst.
    dst = Vault(dst_path, dst_password)
    for key in all_keys:
        if dst.get(key) is not None:
            src.delete(key)

    return written
