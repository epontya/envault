"""Audit log for tracking vault operations."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

DEFAULT_AUDIT_FILE = Path.home() / ".envault" / "audit.log"


class AuditLog:
    """Records vault operations to a local append-only log file."""

    def __init__(self, log_path: Path = DEFAULT_AUDIT_FILE) -> None:
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def record(
        self,
        action: str,
        vault_path: str,
        key: Optional[str] = None,
        profile: Optional[str] = None,
        success: bool = True,
    ) -> None:
        """Append a single audit entry as a JSON line."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "vault": str(vault_path),
            "key": key,
            "profile": profile,
            "success": success,
            "user": os.environ.get("USER") or os.environ.get("USERNAME", "unknown"),
        }
        with self.log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")

    def read(self, limit: int = 100) -> List[dict]:
        """Return the last *limit* audit entries, oldest first."""
        if not self.log_path.exists():
            return []
        lines = self.log_path.read_text(encoding="utf-8").splitlines()
        return [json.loads(line) for line in lines[-limit:] if line.strip()]

    def clear(self) -> None:
        """Erase all audit entries."""
        if self.log_path.exists():
            self.log_path.write_text("", encoding="utf-8")
