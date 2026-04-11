"""Tag management for vault entries — assign, query, and filter by tags."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


class TagError(Exception):
    """Raised when a tagging operation fails."""


class TagStore:
    """Persists a mapping of key -> [tags] alongside a vault file."""

    def __init__(self, tag_file: Path) -> None:
        self._path = tag_file
        self._data: Dict[str, List[str]] = self._load()

    # ------------------------------------------------------------------
    # persistence
    # ------------------------------------------------------------------

    def _load(self) -> Dict[str, List[str]]:
        if self._path.exists():
            return json.loads(self._path.read_text(encoding="utf-8"))
        return {}

    def _save(self) -> None:
        self._path.write_text(
            json.dumps(self._data, indent=2, sort_keys=True), encoding="utf-8"
        )

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------

    def add(self, key: str, tag: str) -> None:
        """Add *tag* to *key*.  Duplicate tags are silently ignored."""
        tags = self._data.setdefault(key, [])
        if tag not in tags:
            tags.append(tag)
            self._save()

    def remove(self, key: str, tag: str) -> bool:
        """Remove *tag* from *key*.  Returns True if the tag existed."""
        tags = self._data.get(key, [])
        if tag in tags:
            tags.remove(tag)
            if not tags:
                del self._data[key]
            self._save()
            return True
        return False

    def get(self, key: str) -> List[str]:
        """Return all tags for *key* (empty list if none)."""
        return list(self._data.get(key, []))

    def keys_for_tag(self, tag: str) -> List[str]:
        """Return all keys that carry *tag*, sorted alphabetically."""
        return sorted(k for k, tags in self._data.items() if tag in tags)

    def clear_key(self, key: str) -> None:
        """Remove all tags associated with *key*."""
        if key in self._data:
            del self._data[key]
            self._save()

    def all_tags(self) -> List[str]:
        """Return a sorted, deduplicated list of every tag in the store."""
        return sorted({tag for tags in self._data.values() for tag in tags})
