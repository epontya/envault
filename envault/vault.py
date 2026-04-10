"""Vault management: create, load, and persist encrypted vaults."""

import json
import os
from pathlib import Path
from typing import Dict, Optional

from envault.crypto import encrypt, decrypt

DEFAULT_VAULT_DIR = Path.home() / ".envault"
VAULT_EXTENSION = ".vault"


class VaultNotFoundError(Exception):
    """Raised when a vault file does not exist."""


class Vault:
    """Represents an encrypted collection of environment variables."""

    def __init__(self, name: str, vault_dir: Optional[Path] = None):
        self.name = name
        self.vault_dir = vault_dir or DEFAULT_VAULT_DIR
        self.path = self.vault_dir / f"{name}{VAULT_EXTENSION}"
        self._data: Dict[str, str] = {}

    def set(self, key: str, value: str) -> None:
        """Set an environment variable in the vault."""
        self._data[key] = value

    def get(self, key: str) -> Optional[str]:
        """Get an environment variable from the vault."""
        return self._data.get(key)

    def delete(self, key: str) -> bool:
        """Delete a key from the vault. Returns True if removed."""
        if key in self._data:
            del self._data[key]
            return True
        return False

    def list_keys(self) -> list:
        """Return all keys stored in the vault."""
        return list(self._data.keys())

    def save(self, password: str) -> None:
        """Encrypt and persist the vault to disk."""
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        plaintext = json.dumps(self._data).encode()
        ciphertext = encrypt(password, plaintext)
        self.path.write_bytes(ciphertext)

    def load(self, password: str) -> None:
        """Load and decrypt the vault from disk."""
        if not self.path.exists():
            raise VaultNotFoundError(f"Vault '{self.name}' not found at {self.path}")
        ciphertext = self.path.read_bytes()
        plaintext = decrypt(password, ciphertext)
        self._data = json.loads(plaintext.decode())

    @classmethod
    def exists(cls, name: str, vault_dir: Optional[Path] = None) -> bool:
        """Check whether a named vault file exists on disk."""
        vault_dir = vault_dir or DEFAULT_VAULT_DIR
        return (vault_dir / f"{name}{VAULT_EXTENSION}").exists()
