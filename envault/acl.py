"""Access Control List (ACL) support for vault keys."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


class ACLError(Exception):
    """Raised when an ACL operation fails."""


ACL_FILE = ".envault_acl.json"


class ACLStore:
    """Stores per-key read/write permission sets keyed by role name."""

    def __init__(self, acl_path: Path) -> None:
        self._path = acl_path
        self._data: Dict[str, Dict[str, List[str]]] = self._load()

    def _load(self) -> Dict[str, Dict[str, List[str]]]:
        if self._path.exists():
            return json.loads(self._path.read_text())
        return {}

    def _save(self) -> None:
        self._path.write_text(json.dumps(self._data, indent=2))

    def grant(self, key: str, role: str, permission: str) -> None:
        """Grant *permission* ('read' or 'write') on *key* to *role*."""
        if permission not in ("read", "write"):
            raise ACLError(f"Invalid permission '{permission}'; use 'read' or 'write'.")
        self._data.setdefault(key, {}).setdefault(role, [])
        if permission not in self._data[key][role]:
            self._data[key][role].append(permission)
        self._save()

    def revoke(self, key: str, role: str, permission: str) -> bool:
        """Revoke *permission* from *role* on *key*. Returns True if removed."""
        try:
            perms = self._data[key][role]
        except KeyError:
            return False
        if permission in perms:
            perms.remove(permission)
            if not perms:
                del self._data[key][role]
            if not self._data[key]:
                del self._data[key]
            self._save()
            return True
        return False

    def can(self, key: str, role: str, permission: str) -> bool:
        """Return True if *role* has *permission* on *key*."""
        return permission in self._data.get(key, {}).get(role, [])

    def permissions(self, key: str, role: str) -> List[str]:
        """Return list of permissions *role* has on *key*."""
        return list(self._data.get(key, {}).get(role, []))

    def roles_for_key(self, key: str) -> Dict[str, List[str]]:
        """Return all role -> permission mappings for *key*."""
        return dict(self._data.get(key, {}))

    def remove_key(self, key: str) -> bool:
        """Remove all ACL entries for *key*. Returns True if anything was removed."""
        if key in self._data:
            del self._data[key]
            self._save()
            return True
        return False
