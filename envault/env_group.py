"""Group multiple vault keys under a named group for bulk operations."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List, Optional


class GroupError(Exception):
    pass


def _group_path(vault_path: Path) -> Path:
    return vault_path.with_suffix(".groups.json")


def _load(vault_path: Path) -> Dict[str, List[str]]:
    p = _group_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(vault_path: Path, data: Dict[str, List[str]]) -> None:
    _group_path(vault_path).write_text(json.dumps(data, indent=2))


def create_group(vault_path: Path, group: str, keys: List[str]) -> List[str]:
    """Create or replace a group with the given keys."""
    if not group:
        raise GroupError("Group name must not be empty.")
    if not keys:
        raise GroupError("Group must contain at least one key.")
    data = _load(vault_path)
    data[group] = list(dict.fromkeys(keys))  # deduplicate, preserve order
    _save(vault_path, data)
    return data[group]


def get_group(vault_path: Path, group: str) -> Optional[List[str]]:
    return _load(vault_path).get(group)


def remove_group(vault_path: Path, group: str) -> bool:
    data = _load(vault_path)
    if group not in data:
        return False
    del data[group]
    _save(vault_path, data)
    return True


def list_groups(vault_path: Path) -> Dict[str, List[str]]:
    return _load(vault_path)


def add_key_to_group(vault_path: Path, group: str, key: str) -> List[str]:
    data = _load(vault_path)
    if group not in data:
        raise GroupError(f"Group '{group}' does not exist.")
    if key not in data[group]:
        data[group].append(key)
        _save(vault_path, data)
    return data[group]


def remove_key_from_group(vault_path: Path, group: str, key: str) -> bool:
    data = _load(vault_path)
    if group not in data or key not in data[group]:
        return False
    data[group].remove(key)
    _save(vault_path, data)
    return True
