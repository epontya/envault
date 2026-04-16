"""Merge multiple vaults into one, with configurable conflict resolution."""
from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from envault.vault import Vault


class MergeError(Exception):
    """Raised when a merge operation fails."""


class ConflictStrategy(str, Enum):
    FIRST = "first"   # keep value from the first vault that defines the key
    LAST = "last"     # keep value from the last vault that defines the key
    RAISE = "raise"   # raise MergeError on conflict


def merge_vaults(
    sources: List[Tuple[Path, str]],
    dest: Vault,
    strategy: ConflictStrategy = ConflictStrategy.LAST,
    overwrite: bool = True,
) -> Dict[str, str]:
    """Merge entries from *sources* into *dest*.

    Parameters
    ----------
    sources:
        List of (vault_path, password) tuples to read from, in order.
    dest:
        Open Vault to write merged entries into.
    strategy:
        How to handle keys that appear in more than one source vault.
    overwrite:
        Whether to overwrite keys already present in *dest*.

    Returns
    -------
    dict mapping every key to the value that was written.
    """
    accumulated: Dict[str, str] = {}

    for vault_path, password in sources:
        src = Vault(vault_path, password)
        for key in src.keys():
            value = src.get(key)
            if value is None:
                continue
            if key in accumulated:
                if strategy is ConflictStrategy.RAISE:
                    raise MergeError(
                        f"Conflict: key '{key}' appears in multiple source vaults."
                    )
                if strategy is ConflictStrategy.FIRST:
                    continue  # keep existing
                # LAST: fall through to overwrite
            accumulated[key] = value

    written: Dict[str, str] = {}
    for key, value in accumulated.items():
        existing = dest.get(key)
        if existing is not None and not overwrite:
            continue
        dest.set(key, value)
        written[key] = value

    return written


def merge_dicts(
    dicts: List[Dict[str, str]],
    strategy: ConflictStrategy = ConflictStrategy.LAST,
) -> Dict[str, str]:
    """Pure-dict merge helper (no I/O)."""
    result: Dict[str, str] = {}
    for d in dicts:
        for key, value in d.items():
            if key in result:
                if strategy is ConflictStrategy.RAISE:
                    raise MergeError(f"Conflict: key '{key}' found in multiple sources.")
                if strategy is ConflictStrategy.FIRST:
                    continue
            result[key] = value
    return result
