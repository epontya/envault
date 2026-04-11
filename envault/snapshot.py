"""Snapshot support: capture and restore vault state at a point in time."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, List, Optional

from envault.vault import Vault


class SnapshotError(Exception):
    """Raised when a snapshot operation fails."""


def _snapshot_path(base_dir: Path, name: str) -> Path:
    return base_dir / f"{name}.snap.json"


def save_snapshot(
    vault: Vault,
    name: str,
    snapshot_dir: Path,
    password: str,
) -> Dict:
    """Capture all current vault entries and write them to a snapshot file."""
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    dest = _snapshot_path(snapshot_dir, name)
    if dest.exists():
        raise SnapshotError(f"Snapshot '{name}' already exists at {dest}")

    entries = {key: vault.get(key, password) for key in vault.list_keys()}
    payload = {
        "name": name,
        "created_at": time.time(),
        "entries": entries,
    }
    dest.write_text(json.dumps(payload, indent=2))
    return payload


def load_snapshot(name: str, snapshot_dir: Path) -> Dict:
    """Read a snapshot from disk and return its payload dict."""
    src = _snapshot_path(snapshot_dir, name)
    if not src.exists():
        raise SnapshotError(f"Snapshot '{name}' not found at {src}")
    return json.loads(src.read_text())


def restore_snapshot(
    vault: Vault,
    name: str,
    snapshot_dir: Path,
    password: str,
    overwrite: bool = True,
) -> int:
    """Restore vault entries from a snapshot. Returns number of keys restored."""
    payload = load_snapshot(name, snapshot_dir)
    entries: Dict[str, str] = payload.get("entries", {})
    for key, value in entries.items():
        if not overwrite and vault.get(key, password) is not None:
            continue
        vault.set(key, value, password)
    return len(entries)


def list_snapshots(snapshot_dir: Path) -> List[str]:
    """Return sorted list of snapshot names found in snapshot_dir."""
    if not snapshot_dir.exists():
        return []
    return sorted(
        p.name.removesuffix(".snap.json")
        for p in snapshot_dir.glob("*.snap.json")
    )


def delete_snapshot(name: str, snapshot_dir: Path) -> bool:
    """Delete a snapshot by name. Returns True if deleted, False if not found."""
    dest = _snapshot_path(snapshot_dir, name)
    if not dest.exists():
        return False
    dest.unlink()
    return True
