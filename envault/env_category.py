"""Category management for vault keys."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


class CategoryError(Exception):
    """Raised when a category operation fails."""


def _category_path(vault_path: str) -> Path:
    p = Path(vault_path)
    return p.parent / f".{p.stem}_categories.json"


def _load(vault_path: str) -> Dict[str, str]:
    cp = _category_path(vault_path)
    if not cp.exists():
        return {}
    return json.loads(cp.read_text())


def _save(vault_path: str, data: Dict[str, str]) -> None:
    _category_path(vault_path).write_text(json.dumps(data, indent=2))


def assign_category(vault_path: str, key: str, category: str) -> str:
    """Assign a category to a key. Returns the category name."""
    if not key:
        raise CategoryError("key must not be empty")
    if not category:
        raise CategoryError("category must not be empty")
    data = _load(vault_path)
    data[key] = category
    _save(vault_path, data)
    return category


def get_category(vault_path: str, key: str) -> Optional[str]:
    """Return the category for a key, or None if not assigned."""
    return _load(vault_path).get(key)


def remove_category(vault_path: str, key: str) -> bool:
    """Remove category assignment for a key. Returns True if removed."""
    data = _load(vault_path)
    if key not in data:
        return False
    del data[key]
    _save(vault_path, data)
    return True


def list_by_category(vault_path: str, category: str) -> List[str]:
    """Return all keys assigned to the given category, sorted."""
    data = _load(vault_path)
    return sorted(k for k, v in data.items() if v == category)


def list_categories(vault_path: str) -> List[str]:
    """Return all distinct category names, sorted."""
    data = _load(vault_path)
    return sorted(set(data.values()))
