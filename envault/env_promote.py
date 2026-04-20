"""Promote environment variables from one vault to another (e.g. staging -> production)."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from envault.vault import Vault, VaultNotFoundError


class PromoteError(Exception):
    """Raised when a promotion operation fails."""


def promote_entries(
    src_path: Path,
    dst_path: Path,
    src_password: str,
    dst_password: str,
    keys: Optional[list[str]] = None,
    overwrite: bool = False,
) -> dict[str, str]:
    """Copy entries from *src_path* vault into *dst_path* vault.

    Parameters
    ----------
    src_path:     Path to the source vault file.
    dst_path:     Path to the destination vault file.
    src_password: Master password for the source vault.
    dst_password: Master password for the destination vault.
    keys:         Explicit list of keys to promote; ``None`` means all keys.
    overwrite:    When *False* (default) existing keys in the destination are
                  left untouched.  When *True* they are overwritten.

    Returns
    -------
    A mapping of ``{key: "promoted" | "skipped"}`` describing what happened
    to each candidate key.
    """
    if not src_path.exists():
        raise VaultNotFoundError(f"Source vault not found: {src_path}")
    if not dst_path.exists():
        raise VaultNotFoundError(f"Destination vault not found: {dst_path}")

    src = Vault(src_path, src_password)
    dst = Vault(dst_path, dst_password)

    all_keys = src.list()
    if not all_keys:
        return {}

    candidates = keys if keys is not None else all_keys
    unknown = [k for k in candidates if k not in all_keys]
    if unknown:
        raise PromoteError(f"Keys not found in source vault: {unknown}")

    result: dict[str, str] = {}
    for key in candidates:
        if not overwrite and dst.get(key) is not None:
            result[key] = "skipped"
            continue
        value = src.get(key)
        dst.set(key, value)  # type: ignore[arg-type]
        result[key] = "promoted"

    return result
