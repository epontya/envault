"""Tests for envault/env_scope.py"""

from __future__ import annotations

import pytest

from envault.env_scope import (
    ScopeError,
    assign_scope,
    get_scopes,
    keys_in_scope,
    list_scopes,
    remove_scope,
    _scope_path,
)


@pytest.fixture()
def vpath(tmp_path):
    return str(tmp_path / "vault.db")


def test_assign_scope_creates_file(vpath):
    assign_scope(vpath, "DB_URL", "dev")
    assert _scope_path(vpath).exists()


def test_assign_scope_returns_sorted_scopes(vpath):
    assign_scope(vpath, "DB_URL", "prod")
    result = assign_scope(vpath, "DB_URL", "dev")
    assert result == ["dev", "prod"]


def test_assign_scope_duplicate_ignored(vpath):
    assign_scope(vpath, "KEY", "staging")
    result = assign_scope(vpath, "KEY", "staging")
    assert result.count("staging") == 1


def test_assign_scope_empty_key_raises(vpath):
    with pytest.raises(ScopeError):
        assign_scope(vpath, "", "dev")


def test_assign_scope_empty_scope_raises(vpath):
    with pytest.raises(ScopeError):
        assign_scope(vpath, "KEY", "")


def test_get_scopes_returns_assigned(vpath):
    assign_scope(vpath, "API_KEY", "dev")
    assign_scope(vpath, "API_KEY", "prod")
    assert get_scopes(vpath, "API_KEY") == ["dev", "prod"]


def test_get_scopes_missing_key_returns_empty(vpath):
    assert get_scopes(vpath, "MISSING") == []


def test_remove_scope_returns_true_when_existed(vpath):
    assign_scope(vpath, "TOKEN", "dev")
    assert remove_scope(vpath, "TOKEN", "dev") is True


def test_remove_scope_returns_false_when_not_present(vpath):
    assert remove_scope(vpath, "TOKEN", "dev") is False


def test_remove_scope_cleans_up_empty_key(vpath):
    assign_scope(vpath, "TOKEN", "dev")
    remove_scope(vpath, "TOKEN", "dev")
    assert get_scopes(vpath, "TOKEN") == []


def test_keys_in_scope_returns_sorted(vpath):
    assign_scope(vpath, "Z_KEY", "staging")
    assign_scope(vpath, "A_KEY", "staging")
    assert keys_in_scope(vpath, "staging") == ["A_KEY", "Z_KEY"]


def test_keys_in_scope_excludes_other_scopes(vpath):
    assign_scope(vpath, "DB_URL", "dev")
    assign_scope(vpath, "SECRET", "prod")
    assert keys_in_scope(vpath, "dev") == ["DB_URL"]


def test_list_scopes_returns_all_distinct(vpath):
    assign_scope(vpath, "K1", "dev")
    assign_scope(vpath, "K2", "prod")
    assign_scope(vpath, "K3", "dev")
    assert list_scopes(vpath) == ["dev", "prod"]


def test_list_scopes_empty_vault_returns_empty(vpath):
    assert list_scopes(vpath) == []
