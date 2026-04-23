"""Generate human-readable diff reports between two sets of env vars."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


class DiffReportError(Exception):
    """Raised when a diff report cannot be generated."""


@dataclass
class DiffReportEntry:
    key: str
    status: str          # 'added' | 'removed' | 'changed' | 'unchanged'
    old_value: Optional[str] = None
    new_value: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "status": self.status,
            "old_value": self.old_value,
            "new_value": self.new_value,
        }


@dataclass
class DiffReport:
    entries: List[DiffReportEntry] = field(default_factory=list)

    @property
    def added(self) -> List[DiffReportEntry]:
        return [e for e in self.entries if e.status == "added"]

    @property
    def removed(self) -> List[DiffReportEntry]:
        return [e for e in self.entries if e.status == "removed"]

    @property
    def changed(self) -> List[DiffReportEntry]:
        return [e for e in self.entries if e.status == "changed"]

    @property
    def unchanged(self) -> List[DiffReportEntry]:
        return [e for e in self.entries if e.status == "unchanged"]

    def has_differences(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    def summary(self) -> str:
        parts = []
        if self.added:
            parts.append(f"+{len(self.added)} added")
        if self.removed:
            parts.append(f"-{len(self.removed)} removed")
        if self.changed:
            parts.append(f"~{len(self.changed)} changed")
        if not parts:
            return "No differences found."
        return ", ".join(parts)

    def to_text(self, show_values: bool = False, redact: bool = True) -> str:
        lines: List[str] = []
        for e in sorted(self.entries, key=lambda x: x.key):
            if e.status == "added":
                val = f" = {e.new_value}" if show_values and not redact else ""
                lines.append(f"  + {e.key}{val}")
            elif e.status == "removed":
                val = f" = {e.old_value}" if show_values and not redact else ""
                lines.append(f"  - {e.key}{val}")
            elif e.status == "changed":
                if show_values and not redact:
                    lines.append(f"  ~ {e.key}: {e.old_value!r} -> {e.new_value!r}")
                else:
                    lines.append(f"  ~ {e.key}")
        return "\n".join(lines) if lines else "  (no differences)"


def build_report(
    old: Dict[str, str],
    new: Dict[str, str],
    include_unchanged: bool = False,
) -> DiffReport:
    """Compare two dicts and return a DiffReport."""
    all_keys = set(old) | set(new)
    entries: List[DiffReportEntry] = []
    for key in sorted(all_keys):
        if key in old and key not in new:
            entries.append(DiffReportEntry(key=key, status="removed", old_value=old[key]))
        elif key not in old and key in new:
            entries.append(DiffReportEntry(key=key, status="added", new_value=new[key]))
        elif old[key] != new[key]:
            entries.append(DiffReportEntry(key=key, status="changed", old_value=old[key], new_value=new[key]))
        elif include_unchanged:
            entries.append(DiffReportEntry(key=key, status="unchanged", old_value=old[key], new_value=new[key]))
    return DiffReport(entries=entries)
