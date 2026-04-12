"""Namespace support for grouping vault keys under logical prefixes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


class NamespaceError(Exception):
    """Raised when a namespace operation fails."""


class NamespaceStore:
    """Maps keys to namespaces and provides prefix-based lookups."""

    def __init__(self, store_path: Path) -> None:
        self._path = store_path
        self._data: Dict[str, str] = self._load()

    def _load(self) -> Dict[str, str]:
        if self._path.exists():
            return json.loads(self._path.read_text())
        return {}

    def _save(self) -> None:
        self._path.write_text(json.dumps(self._data, indent=2))

    def assign(self, key: str, namespace: str) -> None:
        """Assign *key* to *namespace*, overwriting any previous assignment."""
        if not key:
            raise NamespaceError("Key must not be empty.")
        if not namespace:
            raise NamespaceError("Namespace must not be empty.")
        self._data[key] = namespace
        self._save()

    def get_namespace(self, key: str) -> Optional[str]:
        """Return the namespace for *key*, or ``None`` if unassigned."""
        return self._data.get(key)

    def keys_in(self, namespace: str) -> List[str]:
        """Return all keys assigned to *namespace*, sorted."""
        return sorted(k for k, ns in self._data.items() if ns == namespace)

    def list_namespaces(self) -> List[str]:
        """Return a sorted list of all distinct namespaces."""
        return sorted(set(self._data.values()))

    def unassign(self, key: str) -> bool:
        """Remove the namespace assignment for *key*. Returns True if removed."""
        if key in self._data:
            del self._data[key]
            self._save()
            return True
        return False

    def rename(self, old: str, new: str) -> int:
        """Rename all assignments from *old* namespace to *new*. Returns count."""
        if not new:
            raise NamespaceError("New namespace name must not be empty.")
        count = 0
        for key, ns in self._data.items():
            if ns == old:
                self._data[key] = new
                count += 1
        if count:
            self._save()
        return count
