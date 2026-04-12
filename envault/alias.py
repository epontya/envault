"""Key alias support: map short names to full vault keys."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


class AliasError(Exception):
    """Raised when an alias operation fails."""


class AliasStore:
    """Persist and resolve key aliases for a vault."""

    def __init__(self, alias_file: Path) -> None:
        self._path = alias_file
        self._data: Dict[str, str] = self._load()

    def _load(self) -> Dict[str, str]:
        if self._path.exists():
            return json.loads(self._path.read_text())
        return {}

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._data, indent=2))

    def add(self, alias: str, key: str) -> None:
        """Register *alias* as a short-hand for *key*."""
        if not alias or not alias.isidentifier():
            raise AliasError(f"Invalid alias name: {alias!r}")
        if not key:
            raise AliasError("Target key must not be empty.")
        if alias in self._data:
            raise AliasError(
                f"Alias {alias!r} already exists (points to {self._data[alias]!r}). "
                "Remove it first."
            )
        self._data[alias] = key
        self._save()

    def remove(self, alias: str) -> bool:
        """Delete *alias*. Returns True if it existed."""
        if alias not in self._data:
            return False
        del self._data[alias]
        self._save()
        return True

    def resolve(self, alias: str) -> Optional[str]:
        """Return the key that *alias* points to, or None."""
        return self._data.get(alias)

    def list_aliases(self) -> List[tuple[str, str]]:
        """Return sorted list of (alias, key) pairs."""
        return sorted(self._data.items())

    def exists(self, alias: str) -> bool:
        return alias in self._data
