"""Attach human-readable comments/annotations to vault keys."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional


class CommentError(Exception):
    """Raised when a comment operation fails."""


def _comment_path(vault_path: str) -> Path:
    p = Path(vault_path)
    return p.parent / f".{p.stem}_comments.json"


def _load(vault_path: str) -> Dict[str, str]:
    cp = _comment_path(vault_path)
    if not cp.exists():
        return {}
    try:
        return json.loads(cp.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        raise CommentError(f"Failed to load comments: {exc}") from exc


def _save(vault_path: str, data: Dict[str, str]) -> None:
    cp = _comment_path(vault_path)
    try:
        cp.write_text(json.dumps(data, indent=2, sort_keys=True))
    except OSError as exc:
        raise CommentError(f"Failed to save comments: {exc}") from exc


def set_comment(vault_path: str, key: str, comment: str) -> str:
    """Attach *comment* to *key*. Returns the stored comment."""
    if not key:
        raise CommentError("Key must not be empty.")
    data = _load(vault_path)
    data[key] = comment
    _save(vault_path, data)
    return comment


def get_comment(vault_path: str, key: str) -> Optional[str]:
    """Return the comment for *key*, or None if not set."""
    return _load(vault_path).get(key)


def remove_comment(vault_path: str, key: str) -> bool:
    """Remove the comment for *key*. Returns True if it existed."""
    data = _load(vault_path)
    if key not in data:
        return False
    del data[key]
    _save(vault_path, data)
    return True


def list_comments(vault_path: str) -> Dict[str, str]:
    """Return all key→comment mappings for the vault."""
    return dict(_load(vault_path))
