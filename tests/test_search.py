"""Tests for envault.search module."""

from __future__ import annotations

import pytest

from envault.vault import Vault
from envault.search import SearchError, search_keys, search_values


@pytest.fixture()
def vault(tmp_path):
    """A pre-populated vault for search tests."""
    v = Vault(tmp_path / "search_test.vault", password="test")
    v.set("DB_HOST", "localhost")
    v.set("DB_PORT", "5432")
    v.set("DB_PASSWORD", "s3cr3t")
    v.set("API_KEY", "abc123")
    v.set("API_SECRET", "xyz789")
    v.set("DEBUG", "true")
    return v


# ---------------------------------------------------------------------------
# search_keys
# ---------------------------------------------------------------------------

def test_search_keys_glob_prefix(vault):
    results = search_keys(vault, "DB_*")
    assert set(results.keys()) == {"DB_HOST", "DB_PORT", "DB_PASSWORD"}


def test_search_keys_glob_contains(vault):
    results = search_keys(vault, "*SECRET*")
    assert set(results.keys()) == {"API_SECRET"}


def test_search_keys_no_match_returns_empty(vault):
    results = search_keys(vault, "MISSING_*")
    assert results == {}


def test_search_keys_case_insensitive_by_default(vault):
    results = search_keys(vault, "db_*")
    assert set(results.keys()) == {"DB_HOST", "DB_PORT", "DB_PASSWORD"}


def test_search_keys_case_sensitive_no_match(vault):
    results = search_keys(vault, "db_*", case_sensitive=True)
    assert results == {}


def test_search_keys_returns_correct_values(vault):
    results = search_keys(vault, "DB_HOST")
    assert results == {"DB_HOST": "localhost"}


def test_search_keys_wildcard_all(vault):
    results = search_keys(vault, "*")
    assert len(results) == 6


# ---------------------------------------------------------------------------
# search_values
# ---------------------------------------------------------------------------

def test_search_values_substring(vault):
    results = search_values(vault, "localhost")
    assert results == {"DB_HOST": "localhost"}


def test_search_values_partial_match(vault):
    results = search_values(vault, "abc")
    assert "API_KEY" in results


def test_search_values_case_insensitive_by_default(vault):
    results = search_values(vault, "S3CR3T")
    assert "DB_PASSWORD" in results


def test_search_values_case_sensitive_no_match(vault):
    results = search_values(vault, "S3CR3T", case_sensitive=True)
    assert results == {}


def test_search_values_regex(vault):
    results = search_values(vault, r"^\d+$", regex=True)
    assert results == {"DB_PORT": "5432"}


def test_search_values_regex_no_match(vault):
    results = search_values(vault, r"^ZZZ", regex=True)
    assert results == {}


def test_search_values_invalid_regex_raises(vault):
    with pytest.raises(SearchError, match="Invalid regex"):
        search_values(vault, "[invalid", regex=True)


def test_search_values_no_match_returns_empty(vault):
    results = search_values(vault, "nothinghere")
    assert results == {}
