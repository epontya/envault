"""Vault locking: temporarily lock a vault requiring PIN or password to unlock."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional


class LockError(Exception):
    """Raised when a lock operation fails."""


LOCK_FILENAME = ".vault.lock"


def _lock_path(vault_path: Path) -> Path:
    return vault_path.parent / LOCK_FILENAME


def lock_vault(vault_path: Path, reason: str = "manual") -> dict:
    """Create a lock file next to the vault. Returns the lock record."""
    lock_file = _lock_path(vault_path)
    record = {
        "locked_at": time.time(),
        "reason": reason,
        "vault": str(vault_path.name),
    }
    lock_file.write_text(json.dumps(record))
    return record


def unlock_vault(vault_path: Path) -> bool:
    """Remove the lock file. Returns True if a lock existed, False otherwise."""
    lock_file = _lock_path(vault_path)
    if lock_file.exists():
        lock_file.unlink()
        return True
    return False


def is_locked(vault_path: Path) -> bool:
    """Return True if the vault currently has a lock file."""
    return _lock_path(vault_path).exists()


def lock_info(vault_path: Path) -> Optional[dict]:
    """Return the lock record dict, or None if not locked."""
    lock_file = _lock_path(vault_path)
    if not lock_file.exists():
        return None
    try:
        return json.loads(lock_file.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        raise LockError(f"Corrupt lock file: {exc}") from exc


def assert_unlocked(vault_path: Path) -> None:
    """Raise LockError if the vault is locked."""
    info = lock_info(vault_path)
    if info is not None:
        locked_at = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(info.get("locked_at", 0))
        )
        raise LockError(
            f"Vault is locked (since {locked_at}, reason: {info.get('reason', 'unknown')}). "
            "Run 'envault lock unlock' to remove the lock."
        )
