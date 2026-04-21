"""Tests for envault.env_filter."""
from __future__ import annotations

import pytest

from envault.env_filter import (
    FilterError,
    filter_by_key,
    filter_by_prefix,
    filter_by_value,
    filter_keys,
)
from envault.vault import Vault


SAMPLE: dict[str, str] = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "APP_SECRET": "hunter2",
    "APP_DEBUG": "true",
    "REDIS_URL": "redis://localhost",
}


# ---------------------------------------------------------------------------
# filter_by_key
# ---------------------------------------------------------------------------

def test_filter_by_key_glob_prefix():
    result = filter_by_key(SAMPLE, "DB_*")
    assert set(result.keys()) == {"DB_HOST", "DB_PORT"}


def test_filter_by_key_glob_contains():
    result = filter_by_key(SAMPLE, "*SECRET*")
    assert set(result.keys()) == {"APP_SECRET"}


def test_filter_by_key_case_insensitive_default():
    result = filter_by_key(SAMPLE, "app_*")
    assert set(result.keys()) == {"APP_SECRET", "APP_DEBUG"}


def test_filter_by_key_case_sensitive_no_match():
    result = filter_by_key(SAMPLE, "app_*", case_sensitive=True)
    assert result == {}


def test_filter_by_key_empty_pattern_raises():
    with pytest.raises(FilterError):
        filter_by_key(SAMPLE, "")


def test_filter_by_key_no_match_returns_empty():
    result = filter_by_key(SAMPLE, "NONEXISTENT_*")
    assert result == {}


# ---------------------------------------------------------------------------
# filter_by_value
# ---------------------------------------------------------------------------

def test_filter_by_value_substring():
    result = filter_by_value(SAMPLE, "localhost")
    assert set(result.keys()) == {"DB_HOST", "REDIS_URL"}


def test_filter_by_value_case_insensitive_default():
    result = filter_by_value(SAMPLE, "TRUE")
    assert set(result.keys()) == {"APP_DEBUG"}


def test_filter_by_value_case_sensitive():
    result = filter_by_value(SAMPLE, "TRUE", case_sensitive=True)
    assert result == {}


def test_filter_by_value_no_match():
    result = filter_by_value(SAMPLE, "ZZZZ")
    assert result == {}


# ---------------------------------------------------------------------------
# filter_by_prefix
# ---------------------------------------------------------------------------

def test_filter_by_prefix_matches():
    result = filter_by_prefix(SAMPLE, "APP_")
    assert set(result.keys()) == {"APP_SECRET", "APP_DEBUG"}


def test_filter_by_prefix_empty_raises():
    with pytest.raises(FilterError):
        filter_by_prefix(SAMPLE, "")


def test_filter_by_prefix_no_match():
    result = filter_by_prefix(SAMPLE, "XYZ_")
    assert result == {}


# ---------------------------------------------------------------------------
# filter_keys (integration with Vault)
# ---------------------------------------------------------------------------

@pytest.fixture()
def vault_file(tmp_path):
    vpath = str(tmp_path / "vault.db")
    v = Vault(vpath, "secret")
    for key, value in SAMPLE.items():
        v.set(key, value)
    return vpath


def test_filter_keys_by_key_pattern(vault_file):
    result = filter_keys(vault_file, "secret", key_pattern="DB_*")
    assert set(result.keys()) == {"DB_HOST", "DB_PORT"}


def test_filter_keys_by_prefix(vault_file):
    result = filter_keys(vault_file, "secret", prefix="APP_")
    assert set(result.keys()) == {"APP_SECRET", "APP_DEBUG"}


def test_filter_keys_combined(vault_file):
    result = filter_keys(vault_file, "secret", prefix="APP_", value_substring="true")
    assert set(result.keys()) == {"APP_DEBUG"}


def test_filter_keys_no_filters_returns_all(vault_file):
    result = filter_keys(vault_file, "secret")
    assert set(result.keys()) == set(SAMPLE.keys())
