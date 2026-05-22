"""Clone (deep-copy) a vault or a subset of its entries into a new vault file."""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import Iterable, Optional

from envault.vault import Vault, VaultNotFoundError


class CloneError(Exception):
    """Raised when a clone operation fails."""


def clone_vault(
    src_path: Path,
    dst_path: Path,
    password: str,
    *,
    keys: Optional[Iterable[str]] = None,
    overwrite: bool = False,
) -> int:
    """Clone *src_path* into *dst_path*.

    Parameters
    ----------
    src_path:
        Path to the source vault file.
    dst_path:
        Path where the cloned vault will be written.
    password:
        Password used for both reading the source and writing the destination.
    keys:
        Optional subset of keys to copy.  When *None* all entries are copied.
    overwrite:
        When *True* an existing destination vault is replaced entirely.
        When *False* and *dst_path* already exists a :class:`CloneError` is raised.

    Returns
    -------
    int
        Number of entries written to the destination vault.
    """
    if not src_path.exists():
        raise VaultNotFoundError(f"Source vault not found: {src_path}")

    if dst_path.exists() and not overwrite:
        raise CloneError(
            f"Destination vault already exists: {dst_path}. "
            "Pass overwrite=True to replace it."
        )

    src = Vault(src_path, password)
    all_keys = src.list()

    if keys is not None:
        selected = [k for k in keys if k in all_keys]
    else:
        selected = all_keys

    if dst_path.exists() and overwrite:
        dst_path.unlink()

    dst = Vault(dst_path, password)
    for key in selected:
        value = src.get(key)
        if value is not None:
            dst.set(key, value)

    return len(selected)


def clone_vault_file(
    src_path: Path,
    dst_path: Path,
    *,
    overwrite: bool = False,
) -> None:
    """Byte-for-byte copy of a vault file without decrypting it.

    Useful when the caller wants an identical encrypted copy and already knows
    the password will remain the same.
    """
    if not src_path.exists():
        raise VaultNotFoundError(f"Source vault not found: {src_path}")
    if dst_path.exists() and not overwrite:
        raise CloneError(
            f"Destination already exists: {dst_path}. Pass overwrite=True."
        )
    shutil.copy2(src_path, dst_path)
