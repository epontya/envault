"""Integration helpers: wire quota checks into vault set operations."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from envault.quota import QuotaConfig, QuotaError, check_quota
from envault.vault import Vault


def _quota_config_for(vault_path: str) -> QuotaConfig:
    """Return the QuotaConfig associated with a vault file path."""
    return QuotaConfig(Path(vault_path).with_suffix(".quota.json"))


def guarded_set(vault: Vault, vault_path: str, key: str, value: str,
                password: str) -> None:
    """Set a key in the vault, raising QuotaError if limits would be exceeded.

    Parameters
    ----------
    vault:      The open Vault instance.
    vault_path: Filesystem path to the vault file (used to locate quota config).
    key:        The environment variable name.
    value:      The plaintext value to store.
    password:   The vault password (needed to read existing entries for size checks).
    """
    qc = _quota_config_for(vault_path)
    # Read all existing decrypted entries for quota accounting.
    existing = _read_all(vault, password)
    check_quota(qc, existing, key, value)
    vault.set(key, value)


def _read_all(vault: Vault, password: str) -> dict[str, str]:
    """Return all decrypted entries from the vault as a plain dict."""
    result: dict[str, str] = {}
    # Vault.list_keys() returns all stored keys.
    for key in vault.list_keys():
        val: Optional[str] = vault.get(key)
        if val is not None:
            result[key] = val
    return result


def quota_status(vault: Vault, vault_path: str, password: str) -> dict:
    """Return a summary of current usage vs configured limits.

    Returns a dict with keys: entries, total_bytes, limits.
    """
    qc = _quota_config_for(vault_path)
    existing = _read_all(vault, password)
    limits = qc.get_limits()
    total_bytes = sum(len(v.encode()) for v in existing.values())
    return {
        "entries": len(existing),
        "total_bytes": total_bytes,
        "limits": limits,
        "entries_remaining": limits["max_entries"] - len(existing),
        "bytes_remaining": limits["max_total_bytes"] - total_bytes,
    }
