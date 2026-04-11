"""Diff two vault snapshots or a snapshot against the live vault."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envault.vault import Vault
from envault.snapshot import load_snapshot


class DiffError(Exception):
    """Raised when a diff operation fails."""


@dataclass
class DiffResult:
    added: Dict[str, str] = field(default_factory=dict)
    removed: Dict[str, str] = field(default_factory=dict)
    changed: Dict[str, tuple] = field(default_factory=dict)  # key -> (old, new)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    def summary(self) -> str:
        lines: List[str] = []
        for k, v in sorted(self.added.items()):
            lines.append(f"  + {k}={v}")
        for k, v in sorted(self.removed.items()):
            lines.append(f"  - {k}={v}")
        for k, (old, new) in sorted(self.changed.items()):
            lines.append(f"  ~ {k}: {old!r} -> {new!r}")
        return "\n".join(lines) if lines else "  (no changes)"


def diff_dicts(old: Dict[str, str], new: Dict[str, str]) -> DiffResult:
    """Compare two plain key/value dicts and return a DiffResult."""
    result = DiffResult()
    old_keys = set(old)
    new_keys = set(new)

    for k in new_keys - old_keys:
        result.added[k] = new[k]
    for k in old_keys - new_keys:
        result.removed[k] = old[k]
    for k in old_keys & new_keys:
        if old[k] != new[k]:
            result.changed[k] = (old[k], new[k])

    return result


def diff_snapshot_vs_vault(
    vault: Vault,
    password: str,
    snapshot_name: str,
    snap_dir: Optional[str] = None,
) -> DiffResult:
    """Diff a named snapshot (old) against the current vault state (new)."""
    payload = load_snapshot(vault, password, snapshot_name, snap_dir=snap_dir)
    old_data: Dict[str, str] = payload.get("entries", {})
    new_data: Dict[str, str] = {k: vault.get(k, password) for k in vault.list()}
    return diff_dicts(old_data, new_data)


def diff_two_snapshots(
    vault: Vault,
    password: str,
    snap_a: str,
    snap_b: str,
    snap_dir: Optional[str] = None,
) -> DiffResult:
    """Diff two named snapshots (snap_a is old, snap_b is new)."""
    payload_a = load_snapshot(vault, password, snap_a, snap_dir=snap_dir)
    payload_b = load_snapshot(vault, password, snap_b, snap_dir=snap_dir)
    old_data: Dict[str, str] = payload_a.get("entries", {})
    new_data: Dict[str, str] = payload_b.get("entries", {})
    return diff_dicts(old_data, new_data)
