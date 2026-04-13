"""Backup and restore vault files to/from a designated backup directory."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

BACKUP_MANIFEST = "manifest.json"


class BackupError(Exception):
    """Raised when a backup or restore operation fails."""


def _backup_dir(vault_path: Path) -> Path:
    return vault_path.parent / ".envault_backups" / vault_path.stem


def _manifest_path(backup_dir: Path) -> Path:
    return backup_dir / BACKUP_MANIFEST


def _load_manifest(backup_dir: Path) -> dict:
    mp = _manifest_path(backup_dir)
    if not mp.exists():
        return {"backups": []}
    return json.loads(mp.read_text())


def _save_manifest(backup_dir: Path, manifest: dict) -> None:
    _manifest_path(backup_dir).write_text(json.dumps(manifest, indent=2))


def create_backup(vault_path: Path, label: str | None = None) -> dict:
    """Copy the vault file into the backup directory and record metadata."""
    vault_path = Path(vault_path)
    if not vault_path.exists():
        raise BackupError(f"Vault file not found: {vault_path}")

    backup_dir = _backup_dir(vault_path)
    backup_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).isoformat()
    safe_ts = ts.replace(":", "-").replace("+", "Z").split(".")[0] + "Z"
    filename = f"{safe_ts}.vault"
    dest = backup_dir / filename
    shutil.copy2(vault_path, dest)

    entry = {"filename": filename, "created_at": ts, "label": label or ""}
    manifest = _load_manifest(backup_dir)
    manifest["backups"].append(entry)
    _save_manifest(backup_dir, manifest)
    return entry


def list_backups(vault_path: Path) -> list[dict]:
    """Return all backup entries sorted newest-first."""
    backup_dir = _backup_dir(Path(vault_path))
    manifest = _load_manifest(backup_dir)
    return sorted(manifest["backups"], key=lambda e: e["created_at"], reverse=True)


def restore_backup(vault_path: Path, filename: str) -> None:
    """Overwrite the vault file with the named backup."""
    vault_path = Path(vault_path)
    backup_dir = _backup_dir(vault_path)
    src = backup_dir / filename
    if not src.exists():
        raise BackupError(f"Backup not found: {filename}")
    shutil.copy2(src, vault_path)


def delete_backup(vault_path: Path, filename: str) -> None:
    """Remove a single backup file and its manifest entry."""
    backup_dir = _backup_dir(Path(vault_path))
    src = backup_dir / filename
    if not src.exists():
        raise BackupError(f"Backup not found: {filename}")
    src.unlink()
    manifest = _load_manifest(backup_dir)
    manifest["backups"] = [e for e in manifest["backups"] if e["filename"] != filename]
    _save_manifest(backup_dir, manifest)
