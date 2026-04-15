"""Dependency tracking between vault keys."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Set


class DependencyError(Exception):
    """Raised when a dependency operation fails."""


class DependencyStore:
    """Tracks which vault keys depend on other keys."""

    def __init__(self, vault_path: Path) -> None:
        self._path = vault_path.with_suffix(".deps.json")
        self._data: Dict[str, List[str]] = self._load()

    def _load(self) -> Dict[str, List[str]]:
        if self._path.exists():
            return json.loads(self._path.read_text())
        return {}

    def _save(self) -> None:
        self._path.write_text(json.dumps(self._data, indent=2))

    def add(self, key: str, depends_on: str) -> None:
        """Record that *key* depends on *depends_on*."""
        if key == depends_on:
            raise DependencyError("A key cannot depend on itself.")
        deps = self._data.setdefault(key, [])
        if depends_on not in deps:
            deps.append(depends_on)
            self._save()

    def remove(self, key: str, depends_on: str) -> bool:
        """Remove a single dependency edge. Returns True if it existed."""
        deps = self._data.get(key, [])
        if depends_on in deps:
            deps.remove(depends_on)
            if not deps:
                del self._data[key]
            self._save()
            return True
        return False

    def get(self, key: str) -> List[str]:
        """Return all keys that *key* directly depends on."""
        return list(self._data.get(key, []))

    def dependents(self, key: str) -> List[str]:
        """Return all keys that directly depend on *key*."""
        return [k for k, deps in self._data.items() if key in deps]

    def remove_key(self, key: str) -> None:
        """Remove all dependency records for *key* (as dependent or dependency)."""
        self._data.pop(key, None)
        for deps in self._data.values():
            if key in deps:
                deps.remove(key)
        self._save()

    def all_dependencies(self, key: str, _seen: Optional[Set[str]] = None) -> Set[str]:
        """Recursively resolve all transitive dependencies of *key*."""
        if _seen is None:
            _seen = set()
        for dep in self.get(key):
            if dep not in _seen:
                _seen.add(dep)
                self.all_dependencies(dep, _seen)
        return _seen
