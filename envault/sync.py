"""Sync vault contents to/from a remote source (file-based or URL)."""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path
from typing import Dict, Optional

from envault.vault import Vault


class SyncError(Exception):
    """Raised when a sync operation fails."""


def export_vault_data(vault: Vault) -> Dict[str, str]:
    """Return all key/value pairs from *vault* as a plain dict."""
    return {key: vault.get(key) for key in vault.list_keys()}


def import_vault_data(
    vault: Vault,
    data: Dict[str, str],
    *,
    overwrite: bool = True,
) -> int:
    """Write *data* into *vault*.  Returns the number of keys written."""
    written = 0
    for key, value in data.items():
        if not overwrite and vault.get(key) is not None:
            continue
        vault.set(key, value)
        written += 1
    return written


def push_to_file(vault: Vault, dest: Path, password: str) -> None:
    """Encrypt and write vault contents to *dest* as a JSON blob."""
    from envault.crypto import encrypt

    payload = json.dumps(export_vault_data(vault)).encode()
    token = encrypt(password, payload)
    dest.write_bytes(token)


def pull_from_file(
    vault: Vault,
    src: Path,
    password: str,
    *,
    overwrite: bool = True,
) -> int:
    """Decrypt *src* and merge its contents into *vault*."""
    from envault.crypto import decrypt

    if not src.exists():
        raise SyncError(f"Sync source not found: {src}")

    try:
        payload = decrypt(password, src.read_bytes())
    except ValueError as exc:
        raise SyncError(f"Failed to decrypt sync file: {exc}") from exc

    try:
        data: Dict[str, str] = json.loads(payload.decode())
    except json.JSONDecodeError as exc:
        raise SyncError(f"Sync file contains invalid JSON: {exc}") from exc

    return import_vault_data(vault, data, overwrite=overwrite)
