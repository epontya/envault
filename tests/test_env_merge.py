"""Tests for envault.env_merge."""
import pytest
from pathlib import Path

from envault.vault import Vault
from envault.env_merge import (
    ConflictStrategy,
    MergeError,
    merge_dicts,
    merge_vaults,
)


# ---------------------------------------------------------------------------
# merge_dicts (pure, no I/O)
# ---------------------------------------------------------------------------

def test_merge_dicts_last_wins():
    result = merge_dicts([{"A": "1"}, {"A": "2"}], ConflictStrategy.LAST)
    assert result["A"] == "2"


def test_merge_dicts_first_wins():
    result = merge_dicts([{"A": "1"}, {"A": "2"}], ConflictStrategy.FIRST)
    assert result["A"] == "1"


def test_merge_dicts_raise_on_conflict():
    with pytest.raises(MergeError, match="Conflict"):
        merge_dicts([{"A": "1"}, {"A": "2"}], ConflictStrategy.RAISE)


def test_merge_dicts_no_conflict():
    result = merge_dicts([{"A": "1"}, {"B": "2"}])
    assert result == {"A": "1", "B": "2"}


def test_merge_dicts_empty():
    assert merge_dicts([]) == {}


def test_merge_dicts_single():
    assert merge_dicts([{"X": "y"}]) == {"X": "y"}


# ---------------------------------------------------------------------------
# merge_vaults (with real Vault objects)
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_vaults(tmp_path):
    """Return a factory that creates a Vault pre-populated with entries."""
    pw = "testpass"

    def _make(name: str, entries: dict) -> Path:
        p = tmp_path / name
        v = Vault(p, pw)
        for k, val in entries.items():
            v.set(k, val)
        return p

    return _make, pw


def test_merge_vaults_basic(tmp_vaults, tmp_path):
    make, pw = tmp_vaults
    src1 = make("v1.vault", {"KEY1": "aaa", "SHARED": "from_v1"})
    src2 = make("v2.vault", {"KEY2": "bbb", "SHARED": "from_v2"})
    dest = Vault(tmp_path / "dest.vault", pw)

    written = merge_vaults([(src1, pw), (src2, pw)], dest, ConflictStrategy.LAST)

    assert dest.get("KEY1") == "aaa"
    assert dest.get("KEY2") == "bbb"
    assert dest.get("SHARED") == "from_v2"
    assert written["SHARED"] == "from_v2"


def test_merge_vaults_first_strategy(tmp_vaults, tmp_path):
    make, pw = tmp_vaults
    src1 = make("v1.vault", {"SHARED": "first"})
    src2 = make("v2.vault", {"SHARED": "second"})
    dest = Vault(tmp_path / "dest.vault", pw)

    merge_vaults([(src1, pw), (src2, pw)], dest, ConflictStrategy.FIRST)
    assert dest.get("SHARED") == "first"


def test_merge_vaults_raise_strategy(tmp_vaults, tmp_path):
    make, pw = tmp_vaults
    src1 = make("v1.vault", {"SHARED": "x"})
    src2 = make("v2.vault", {"SHARED": "y"})
    dest = Vault(tmp_path / "dest.vault", pw)

    with pytest.raises(MergeError):
        merge_vaults([(src1, pw), (src2, pw)], dest, ConflictStrategy.RAISE)


def test_merge_vaults_no_overwrite_keeps_dest(tmp_vaults, tmp_path):
    make, pw = tmp_vaults
    src = make("src.vault", {"KEY": "new_value"})
    dest = Vault(tmp_path / "dest.vault", pw)
    dest.set("KEY", "original")

    merge_vaults([(src, pw)], dest, overwrite=False)
    assert dest.get("KEY") == "original"
