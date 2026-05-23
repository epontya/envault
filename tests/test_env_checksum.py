"""Tests for envault.env_checksum."""

from __future__ import annotations

from pathlib import Path

import pytest

from envault.env_checksum import (
    ChecksumError,
    compute_checksum,
    load_checksum,
    remove_checksum,
    save_checksum,
    verify_checksum,
)


@pytest.fixture()
def vault_file(tmp_path: Path) -> Path:
    vf = tmp_path / "vault.db"
    vf.write_bytes(b"dummy")  # content irrelevant for checksum tests
    return vf


def test_compute_checksum_returns_hex_string() -> None:
    digest = compute_checksum({"KEY": "value"})
    assert isinstance(digest, str)
    assert len(digest) == 64  # SHA-256 hex


def test_compute_checksum_is_deterministic() -> None:
    data = {"A": "1", "B": "2"}
    assert compute_checksum(data) == compute_checksum(data)


def test_compute_checksum_order_independent() -> None:
    d1 = {"A": "1", "B": "2"}
    d2 = {"B": "2", "A": "1"}
    assert compute_checksum(d1) == compute_checksum(d2)


def test_compute_checksum_differs_for_different_data() -> None:
    assert compute_checksum({"K": "v1"}) != compute_checksum({"K": "v2"})


def test_save_checksum_creates_file(vault_file: Path) -> None:
    save_checksum(vault_file, {"FOO": "bar"})
    cpath = vault_file.with_suffix(".checksum.json")
    assert cpath.exists()


def test_save_checksum_returns_digest(vault_file: Path) -> None:
    data = {"FOO": "bar"}
    digest = save_checksum(vault_file, data)
    assert digest == compute_checksum(data)


def test_load_checksum_returns_none_when_missing(vault_file: Path) -> None:
    assert load_checksum(vault_file) is None


def test_load_checksum_returns_saved_digest(vault_file: Path) -> None:
    data = {"X": "y"}
    digest = save_checksum(vault_file, data)
    assert load_checksum(vault_file) == digest


def test_verify_checksum_true_for_matching_data(vault_file: Path) -> None:
    data = {"DB_URL": "postgres://localhost/mydb"}
    save_checksum(vault_file, data)
    assert verify_checksum(vault_file, data) is True


def test_verify_checksum_false_for_modified_data(vault_file: Path) -> None:
    save_checksum(vault_file, {"DB_URL": "original"})
    assert verify_checksum(vault_file, {"DB_URL": "tampered"}) is False


def test_verify_checksum_raises_when_no_file(vault_file: Path) -> None:
    with pytest.raises(ChecksumError, match="No checksum file"):
        verify_checksum(vault_file, {})


def test_remove_checksum_returns_true_when_existed(vault_file: Path) -> None:
    save_checksum(vault_file, {})
    assert remove_checksum(vault_file) is True


def test_remove_checksum_returns_false_when_missing(vault_file: Path) -> None:
    assert remove_checksum(vault_file) is False


def test_remove_checksum_deletes_file(vault_file: Path) -> None:
    save_checksum(vault_file, {"K": "v"})
    remove_checksum(vault_file)
    assert not vault_file.with_suffix(".checksum.json").exists()
