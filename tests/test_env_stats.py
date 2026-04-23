"""Tests for envault.env_stats."""
from __future__ import annotations

import pytest

from envault.vault import Vault
from envault.env_stats import VaultStats, compute_stats


@pytest.fixture()
def vault(tmp_path):
    v = Vault(tmp_path / "vault.db", password="secret")
    return v


def test_empty_vault_returns_zero_stats(vault):
    stats = compute_stats(vault)
    assert stats.total_keys == 0
    assert stats.total_bytes == 0
    assert stats.empty_values == 0
    assert stats.avg_value_length == 0.0


def test_total_keys(vault):
    vault.set("A", "1")
    vault.set("B", "22")
    vault.set("C", "333")
    stats = compute_stats(vault)
    assert stats.total_keys == 3


def test_empty_value_counted(vault):
    vault.set("KEY", "")
    vault.set("OTHER", "value")
    stats = compute_stats(vault)
    assert stats.empty_values == 1


def test_no_empty_values(vault):
    vault.set("X", "hello")
    stats = compute_stats(vault)
    assert stats.empty_values == 0


def test_avg_value_length(vault):
    vault.set("A", "ab")      # len 2
    vault.set("B", "abcd")    # len 4
    stats = compute_stats(vault)
    assert stats.avg_value_length == pytest.approx(3.0)


def test_max_value_length(vault):
    vault.set("A", "hi")
    vault.set("B", "hello world")
    stats = compute_stats(vault)
    assert stats.max_value_length == len("hello world")


def test_min_value_length(vault):
    vault.set("A", "x")
    vault.set("B", "longer")
    stats = compute_stats(vault)
    assert stats.min_value_length == 1


def test_total_bytes_includes_keys_and_values(vault):
    vault.set("K", "V")   # 1 + 1 = 2
    stats = compute_stats(vault)
    assert stats.total_bytes == 2


def test_longest_and_shortest_key(vault):
    vault.set("A", "v")
    vault.set("LONG_KEY_NAME", "v")
    vault.set("MID", "v")
    stats = compute_stats(vault)
    assert stats.longest_key == "LONG_KEY_NAME"
    assert stats.shortest_key == "A"


def test_summary_contains_labels(vault):
    vault.set("FOO", "bar")
    stats = compute_stats(vault)
    summary = stats.summary()
    assert "Total keys" in summary
    assert "Total bytes" in summary
    assert "Avg value length" in summary
    assert "Longest key" in summary
