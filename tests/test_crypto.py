"""Tests for envault.crypto encryption/decryption module."""

import pytest
from envault.crypto import encrypt, decrypt, derive_key, SALT_SIZE


PASSWORD = "super-secret-passphrase"
PLAINTEXT = "DATABASE_URL=postgres://user:pass@localhost/db\nAPI_KEY=abc123"


def test_encrypt_returns_bytes():
    result = encrypt(PLAINTEXT, PASSWORD)
    assert isinstance(result, bytes)


def test_encrypt_output_longer_than_salt():
    result = encrypt(PLAINTEXT, PASSWORD)
    assert len(result) > SALT_SIZE


def test_round_trip():
    payload = encrypt(PLAINTEXT, PASSWORD)
    recovered = decrypt(payload, PASSWORD)
    assert recovered == PLAINTEXT


def test_different_encryptions_produce_different_ciphertext():
    payload1 = encrypt(PLAINTEXT, PASSWORD)
    payload2 = encrypt(PLAINTEXT, PASSWORD)
    # Random salt means each encryption is unique
    assert payload1 != payload2


def test_wrong_password_raises_value_error():
    payload = encrypt(PLAINTEXT, PASSWORD)
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt(payload, "wrong-password")


def test_corrupted_payload_raises_value_error():
    payload = bytearray(encrypt(PLAINTEXT, PASSWORD))
    payload[20] ^= 0xFF  # flip a byte in the ciphertext
    with pytest.raises(ValueError):
        decrypt(bytes(payload), PASSWORD)


def test_too_short_payload_raises_value_error():
    with pytest.raises(ValueError, match="too short"):
        decrypt(b"short", PASSWORD)


def test_derive_key_is_deterministic():
    salt = b"\x00" * SALT_SIZE
    key1 = derive_key(PASSWORD, salt)
    key2 = derive_key(PASSWORD, salt)
    assert key1 == key2


def test_derive_key_differs_with_different_salt():
    key1 = derive_key(PASSWORD, b"\x00" * SALT_SIZE)
    key2 = derive_key(PASSWORD, b"\xff" * SALT_SIZE)
    assert key1 != key2
