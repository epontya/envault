"""Checksum utilities for detecting vault tampering or drift."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, Optional


class ChecksumError(Exception):
    """Raised when checksum operations fail."""


def _checksum_path(vault_path: Path) -> Path:
    return vault_path.with_suffix(".checksum.json")


def compute_checksum(data: Dict[str, str]) -> str:
    """Return a SHA-256 hex digest of the canonical JSON representation of *data*."""
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def save_checksum(vault_path: Path, data: Dict[str, str]) -> str:
    """Compute and persist a checksum for *data* beside *vault_path*.

    Returns the hex digest that was saved.
    """
    digest = compute_checksum(data)
    record = {"vault": str(vault_path), "sha256": digest}
    _checksum_path(vault_path).write_text(json.dumps(record, indent=2))
    return digest


def load_checksum(vault_path: Path) -> Optional[str]:
    """Return the previously saved checksum for *vault_path*, or ``None``."""
    cpath = _checksum_path(vault_path)
    if not cpath.exists():
        return None
    record = json.loads(cpath.read_text())
    return record.get("sha256")


def verify_checksum(vault_path: Path, data: Dict[str, str]) -> bool:
    """Return ``True`` when *data* matches the stored checksum.

    Raises :class:`ChecksumError` if no checksum file exists.
    """
    stored = load_checksum(vault_path)
    if stored is None:
        raise ChecksumError(
            f"No checksum file found for vault '{vault_path}'. "
            "Run 'envault checksum save' first."
        )
    return compute_checksum(data) == stored


def remove_checksum(vault_path: Path) -> bool:
    """Delete the checksum file for *vault_path*. Returns ``True`` if it existed."""
    cpath = _checksum_path(vault_path)
    if cpath.exists():
        cpath.unlink()
        return True
    return False
