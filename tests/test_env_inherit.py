"""Tests for envault.env_inherit."""
from __future__ import annotations

import pytest
from pathlib import Path

from envault.vault import Vault
from envault.env_inherit import (
    InheritError,
    add_parent,
    list_parents,
    remove_parent,
    resolve_inherited,
)

PASS = "secret"


@pytest.fixture()
def parent_vault(tmp_path: Path) -> Path:
    vp = tmp_path / "parent.vault"
    v = Vault(vp, PASS)
    v.set("SHARED", "from_parent")
    v.set("PARENT_ONLY", "yes")
    return vp


@pytest.fixture()
def child_vault(tmp_path: Path) -> Path:
    vp = tmp_path / "child.vault"
    v = Vault(vp, PASS)
    v.set("SHARED", "from_child")
    v.set("CHILD_ONLY", "yes")
    return vp


def test_add_parent_returns_list(child_vault, parent_vault):
    result = add_parent(child_vault, str(parent_vault))
    assert str(parent_vault) in result


def test_list_parents_empty(child_vault):
    assert list_parents(child_vault) == []


def test_list_parents_after_add(child_vault, parent_vault):
    add_parent(child_vault, str(parent_vault))
    assert str(parent_vault) in list_parents(child_vault)


def test_duplicate_parent_raises(child_vault, parent_vault):
    add_parent(child_vault, str(parent_vault))
    with pytest.raises(InheritError):
        add_parent(child_vault, str(parent_vault))


def test_remove_existing_parent(child_vault, parent_vault):
    add_parent(child_vault, str(parent_vault))
    assert remove_parent(child_vault, str(parent_vault)) is True
    assert list_parents(child_vault) == []


def test_remove_missing_parent_returns_false(child_vault):
    assert remove_parent(child_vault, "/nonexistent") is False


def test_resolve_child_wins_on_conflict(child_vault, parent_vault):
    add_parent(child_vault, str(parent_vault))
    merged = resolve_inherited(child_vault, PASS)
    assert merged["SHARED"] == "from_child"


def test_resolve_inherits_parent_only_key(child_vault, parent_vault):
    add_parent(child_vault, str(parent_vault))
    merged = resolve_inherited(child_vault, PASS)
    assert merged["PARENT_ONLY"] == "yes"


def test_resolve_child_only_key_present(child_vault, parent_vault):
    add_parent(child_vault, str(parent_vault))
    merged = resolve_inherited(child_vault, PASS)
    assert merged["CHILD_ONLY"] == "yes"


def test_resolve_missing_parent_raises(child_vault):
    add_parent(child_vault, "/does/not/exist.vault")
    with pytest.raises(InheritError):
        resolve_inherited(child_vault, PASS)
