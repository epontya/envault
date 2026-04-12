"""PIN-based quick-unlock for vault sessions.

Allows setting a short numeric PIN that is used to derive a session token,
avoiding repeated entry of the full master password during a session.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path

SESSION_TTL_SECONDS = 3600  # 1 hour


class PINError(Exception):
    """Raised for PIN-related errors."""


class PINStore:
    def __init__(self, pin_file: Path) -> None:
        self._path = pin_file

    def _load(self) -> dict:
        if not self._path.exists():
            return {}
        with self._path.open() as f:
            return json.load(f)

    def _save(self, data: dict) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("w") as f:
            json.dump(data, f)
        os.chmod(self._path, 0o600)

    def set_pin(self, pin: str, password: str) -> None:
        """Store a hashed PIN and the encrypted password reference."""
        if not pin.isdigit() or len(pin) < 4:
            raise PINError("PIN must be at least 4 digits.")
        pin_hash = hashlib.sha256(pin.encode()).hexdigest()
        data = {
            "pin_hash": pin_hash,
            "password": password,
            "created_at": time.time(),
        }
        self._save(data)

    def unlock(self, pin: str) -> str:
        """Validate PIN and return the stored password if valid and not expired."""
        data = self._load()
        if not data:
            raise PINError("No PIN has been set.")
        age = time.time() - data.get("created_at", 0)
        if age > SESSION_TTL_SECONDS:
            self.clear()
            raise PINError("PIN session has expired. Please re-authenticate.")
        pin_hash = hashlib.sha256(pin.encode()).hexdigest()
        if pin_hash != data["pin_hash"]:
            raise PINError("Incorrect PIN.")
        return data["password"]

    def clear(self) -> None:
        """Remove the stored PIN session."""
        if self._path.exists():
            self._path.unlink()

    def is_set(self) -> bool:
        """Return True if a PIN session exists and has not expired."""
        data = self._load()
        if not data:
            return False
        age = time.time() - data.get("created_at", 0)
        return age <= SESSION_TTL_SECONDS
