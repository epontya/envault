"""Tests for envault.env_compare."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from envault.vault import Vault
from envault.env_compare import (
    CompareError,
    CompareResult,
    compare_with_dotenv,
    compare_with_env,
)

PASSWORD = "test-password"


@pytest.fixture()
def vault(tmp_path: Path) -> Vault:
    v = Vault(tmp_path / "vault.enc", PASSWORD)
    v.set("KEY_A", "alpha")
    v.set("KEY_B", "beta")
    v.set("KEY_C", "gamma")
    return v


@pytest.fixture()
def dotenv_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text('KEY_A=alpha\nKEY_B=different\nKEY_D=delta\n')
    return p


# --- CompareResult helpers ---

def test_has_differences_false_when_all_match():
    r = CompareResult(matching=["A", "B"])
    assert not r.has_differences()


def test_has_differences_true_when_value_differs():
    r = CompareResult(value_differs=["A"])
    assert r.has_differences()


def test_summary_contains_labels():
    r = CompareResult(
        only_in_vault=["V"],
        only_in_source=["S"],
        value_differs=["D"],
        matching=["M"],
    )
    summary = r.summary()
    assert "only-in-vault" in summary
    assert "only-in-source" in summary
    assert "value-differs" in summary
    assert "match" in summary


def test_summary_empty():
    assert "no entries" in CompareResult().summary()


# --- compare_with_dotenv ---

def test_dotenv_matching_key(vault: Vault, dotenv_file: Path):
    result = compare_with_dotenv(vault, dotenv_file)
    assert "KEY_A" in result.matching


def test_dotenv_value_differs(vault: Vault, dotenv_file: Path):
    result = compare_with_dotenv(vault, dotenv_file)
    assert "KEY_B" in result.value_differs


def test_dotenv_only_in_vault(vault: Vault, dotenv_file: Path):
    result = compare_with_dotenv(vault, dotenv_file)
    assert "KEY_C" in result.only_in_vault


def test_dotenv_only_in_source(vault: Vault, dotenv_file: Path):
    result = compare_with_dotenv(vault, dotenv_file)
    assert "KEY_D" in result.only_in_source


def test_dotenv_missing_file_raises(vault: Vault, tmp_path: Path):
    with pytest.raises(CompareError):
        compare_with_dotenv(vault, tmp_path / "nonexistent.env")


def test_dotenv_key_filter(vault: Vault, dotenv_file: Path):
    result = compare_with_dotenv(vault, dotenv_file, keys=["KEY_A"])
    assert result.matching == ["KEY_A"]
    assert result.value_differs == []
    assert result.only_in_vault == []
    assert result.only_in_source == []


# --- compare_with_env ---

def test_env_matching_key(vault: Vault, monkeypatch):
    monkeypatch.setenv("KEY_A", "alpha")
    result = compare_with_env(vault, keys=["KEY_A"])
    assert "KEY_A" in result.matching


def test_env_value_differs(vault: Vault, monkeypatch):
    monkeypatch.setenv("KEY_B", "wrong")
    result = compare_with_env(vault, keys=["KEY_B"])
    assert "KEY_B" in result.value_differs


def test_env_only_in_vault(vault: Vault, monkeypatch):
    monkeypatch.delenv("KEY_C", raising=False)
    result = compare_with_env(vault, keys=["KEY_C"])
    assert "KEY_C" in result.only_in_vault
