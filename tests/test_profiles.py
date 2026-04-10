"""Tests for envault.profiles."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envault.profiles import ProfileManager, ProfileNotFoundError


@pytest.fixture()
def pm(tmp_path: Path) -> ProfileManager:
    """ProfileManager backed by a temp directory."""
    return ProfileManager(profiles_path=tmp_path / "profiles.json")


def test_add_and_get(pm: ProfileManager, tmp_path: Path) -> None:
    vault = tmp_path / "dev.vault"
    pm.add("dev", vault)
    assert pm.get_path("dev") == vault


def test_list_profiles_sorted(pm: ProfileManager, tmp_path: Path) -> None:
    pm.add("staging", tmp_path / "s.vault")
    pm.add("dev", tmp_path / "d.vault")
    pm.add("prod", tmp_path / "p.vault")
    assert pm.list_profiles() == ["dev", "prod", "staging"]


def test_exists(pm: ProfileManager, tmp_path: Path) -> None:
    pm.add("dev", tmp_path / "dev.vault")
    assert pm.exists("dev") is True
    assert pm.exists("nope") is False


def test_remove_existing(pm: ProfileManager, tmp_path: Path) -> None:
    pm.add("dev", tmp_path / "dev.vault")
    result = pm.remove("dev")
    assert result is True
    assert not pm.exists("dev")


def test_remove_missing_returns_false(pm: ProfileManager) -> None:
    assert pm.remove("ghost") is False


def test_get_missing_raises(pm: ProfileManager) -> None:
    with pytest.raises(ProfileNotFoundError):
        pm.get_path("missing")


def test_rename(pm: ProfileManager, tmp_path: Path) -> None:
    pm.add("old", tmp_path / "old.vault")
    pm.rename("old", "new")
    assert pm.exists("new")
    assert not pm.exists("old")
    assert pm.get_path("new") == tmp_path / "old.vault"


def test_rename_missing_raises(pm: ProfileManager) -> None:
    with pytest.raises(ProfileNotFoundError):
        pm.rename("ghost", "spirit")


def test_persists_to_disk(tmp_path: Path) -> None:
    profiles_file = tmp_path / "profiles.json"
    pm1 = ProfileManager(profiles_path=profiles_file)
    pm1.add("dev", tmp_path / "dev.vault")

    pm2 = ProfileManager(profiles_path=profiles_file)
    assert pm2.exists("dev")
    assert pm2.get_path("dev") == tmp_path / "dev.vault"


def test_file_is_valid_json(tmp_path: Path) -> None:
    profiles_file = tmp_path / "profiles.json"
    pm = ProfileManager(profiles_path=profiles_file)
    pm.add("ci", tmp_path / "ci.vault")
    data = json.loads(profiles_file.read_text())
    assert "ci" in data
