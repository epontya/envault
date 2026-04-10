"""Encryption and decryption utilities for envault vaults."""

import os
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet


SALT_SIZE = 16
ITERATIONS = 480_000


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a Fernet-compatible key from a password and salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
    )
    raw_key = kdf.derive(password.encode())
    return base64.urlsafe_b64encode(raw_key)


def encrypt(data: str, password: str) -> bytes:
    """Encrypt plaintext data with a password.

    Returns salt + ciphertext as a single bytes object.
    """
    salt = os.urandom(SALT_SIZE)
    key = derive_key(password, salt)
    token = Fernet(key).encrypt(data.encode())
    return salt + token


def decrypt(payload: bytes, password: str) -> str:
    """Decrypt payload produced by :func:`encrypt`.

    Raises:
        ValueError: if the password is wrong or data is corrupted.
    """
    if len(payload) <= SALT_SIZE:
        raise ValueError("Invalid payload: too short.")
    salt, token = payload[:SALT_SIZE], payload[SALT_SIZE:]
    key = derive_key(password, salt)
    try:
        return Fernet(key).decrypt(token).decode()
    except Exception as exc:
        raise ValueError("Decryption failed — wrong password or corrupted data.") from exc
