"""Profile management for envault — named collections of vaults per environment."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_PROFILES_FILE = Path.home() / ".envault" / "profiles.json"


class ProfileNotFoundError(KeyError):
    """Raised when a requested profile does not exist."""


class ProfileManager:
    """Manages named profiles that map to vault file paths."""

    def __init__(self, profiles_path: Path = DEFAULT_PROFILES_FILE) -> None:
        self.profiles_path = profiles_path
        self._data: Dict[str, str] = {}
        self._load()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load(self) -> None:
        if self.profiles_path.exists():
            with self.profiles_path.open("r", encoding="utf-8") as fh:
                self._data = json.load(fh)
        else:
            self._data = {}

    def _save(self) -> None:
        self.profiles_path.parent.mkdir(parents=True, exist_ok=True)
        with self.profiles_path.open("w", encoding="utf-8") as fh:
            json.dump(self._data, fh, indent=2)
            fh.write("\n")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add(self, name: str, vault_path: Path) -> None:
        """Register a profile name pointing to *vault_path*."""
        self._data[name] = str(vault_path)
        self._save()

    def remove(self, name: str) -> bool:
        """Remove a profile. Returns True if it existed."""
        if name in self._data:
            del self._data[name]
            self._save()
            return True
        return False

    def get_path(self, name: str) -> Path:
        """Return the vault path for *name*, raising ProfileNotFoundError if absent."""
        if name not in self._data:
            raise ProfileNotFoundError(f"Profile '{name}' not found.")
        return Path(self._data[name])

    def list_profiles(self) -> List[str]:
        """Return sorted list of profile names."""
        return sorted(self._data.keys())

    def exists(self, name: str) -> bool:
        return name in self._data

    def rename(self, old_name: str, new_name: str) -> None:
        """Rename a profile."""
        if old_name not in self._data:
            raise ProfileNotFoundError(f"Profile '{old_name}' not found.")
        self._data[new_name] = self._data.pop(old_name)
        self._save()
