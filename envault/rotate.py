"""Key rotation: re-encrypt vault data under a new password."""

from __future__ import annotations

from pathlib import Path

from envault.vault import Vault, VaultNotFoundError


class RotationError(Exception):
    """Raised when key rotation fails."""


def rotate_vault_password(
    vault_path: Path,
    old_password: str,
    new_password: str,
) -> int:
    """Re-encrypt every entry in *vault_path* using *new_password*.

    Returns the number of entries that were re-encrypted.

    Raises
    ------
    VaultNotFoundError
        If *vault_path* does not exist.
    RotationError
        If decryption with *old_password* fails or the vault cannot be saved.
    ValueError
        If *old_password* or *new_password* are empty strings.
    """
    if not old_password:
        raise ValueError("old_password must not be empty")
    if not new_password:
        raise ValueError("new_password must not be empty")
    if old_password == new_password:
        raise RotationError("new_password must differ from old_password")

    if not vault_path.exists():
        raise VaultNotFoundError(f"Vault not found: {vault_path}")

    # Open with old password to verify we can decrypt everything first.
    old_vault = Vault(vault_path, old_password)
    try:
        all_keys = old_vault.keys()
        plaintext: dict[str, str] = {}
        for key in all_keys:
            value = old_vault.get(key)
            if value is not None:
                plaintext[key] = value
    except ValueError as exc:
        raise RotationError(f"Failed to decrypt vault with old password: {exc}") from exc

    # Write everything back under the new password.
    new_vault = Vault(vault_path, new_password)
    # Overwrite the file from scratch so stale ciphertext is not left behind.
    vault_path.write_bytes(b"")
    for key, value in plaintext.items():
        new_vault.set(key, value)

    return len(plaintext)
