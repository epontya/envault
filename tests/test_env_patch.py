"""Tests for envault.env_patch."""
from __future__ import annotations

import pytest

from envault.vault import Vault
from envault.env_patch import PatchError, apply_patch


PASSWORD = "test-secret"


@pytest.fixture()
def vault(tmp_path):
    v = Vault(str(tmp_path / "vault.db"), PASSWORD)
    v.set("EXISTING", "old_value")
    v.set("TO_DELETE", "bye")
    return v


def test_apply_patch_updates_existing_key(vault):
    summary = apply_patch(vault, {"EXISTING": "new_value"})
    assert vault.get("EXISTING") == "new_value"
    assert "EXISTING" in summary["updated"]


def test_apply_patch_adds_new_key(vault):
    summary = apply_patch(vault, {"BRAND_NEW": "hello"})
    assert vault.get("BRAND_NEW") == "hello"
    assert "BRAND_NEW" in summary["added"]


def test_apply_patch_skips_new_key_when_add_new_false(vault):
    summary = apply_patch(vault, {"BRAND_NEW": "hello"}, add_new=False)
    assert vault.get("BRAND_NEW") is None
    assert summary["added"] == []


def test_apply_patch_removes_null_key(vault):
    summary = apply_patch(vault, {"TO_DELETE": None})
    assert vault.get("TO_DELETE") is None
    assert "TO_DELETE" in summary["removed"]


def test_apply_patch_keeps_null_key_when_remove_nulls_false(vault):
    summary = apply_patch(vault, {"TO_DELETE": None}, remove_nulls=False)
    assert vault.get("TO_DELETE") == "bye"
    assert summary["removed"] == []


def test_apply_patch_mixed_operations(vault):
    summary = apply_patch(
        vault,
        {"EXISTING": "updated", "NEW_KEY": "v", "TO_DELETE": None},
    )
    assert vault.get("EXISTING") == "updated"
    assert vault.get("NEW_KEY") == "v"
    assert vault.get("TO_DELETE") is None
    assert "EXISTING" in summary["updated"]
    assert "NEW_KEY" in summary["added"]
    assert "TO_DELETE" in summary["removed"]


def test_apply_patch_empty_patch_returns_empty_summary(vault):
    summary = apply_patch(vault, {})
    assert summary == {"added": [], "updated": [], "removed": []}


def test_apply_patch_invalid_patch_type_raises(vault):
    with pytest.raises(PatchError):
        apply_patch(vault, "not-a-dict")  # type: ignore[arg-type]


def test_apply_patch_invalid_key_raises(vault):
    with pytest.raises(PatchError):
        apply_patch(vault, {"": "value"})


def test_apply_patch_null_removes_only_existing_key(vault):
    """Removing a key that does not exist should not appear in removed list."""
    summary = apply_patch(vault, {"GHOST": None})
    assert summary["removed"] == []
