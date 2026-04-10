"""envault — securely store and sync environment variables using encrypted local vaults."""

__version__ = "0.1.0"

from envault.vault import Vault, VaultNotFoundError

__all__ = ["Vault", "VaultNotFoundError"]
