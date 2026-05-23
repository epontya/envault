"""env_preview.py – render a human-friendly preview of vault entries."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envault.env_redact import is_sensitive_key, redact_value


class PreviewError(Exception):
    """Raised when preview generation fails."""


@dataclass
class PreviewEntry:
    key: str
    raw_value: str
    display_value: str
    sensitive: bool
    length: int

    def to_dict(self) -> Dict:
        return {
            "key": self.key,
            "display_value": self.display_value,
            "sensitive": self.sensitive,
            "length": self.length,
        }


def build_preview(
    data: Dict[str, str],
    *,
    reveal: bool = False,
    extra_patterns: Optional[List[str]] = None,
    max_value_length: int = 60,
) -> List[PreviewEntry]:
    """Return a list of PreviewEntry objects for *data*.

    Args:
        data: Mapping of key -> plaintext value.
        reveal: If True, sensitive values are shown in full.
        extra_patterns: Additional glob patterns that mark keys as sensitive.
        max_value_length: Truncate display values longer than this.
    """
    if not isinstance(data, dict):
        raise PreviewError("data must be a dict")

    entries: List[PreviewEntry] = []
    for key in sorted(data):
        raw = str(data[key])
        sensitive = is_sensitive_key(key, extra_patterns=extra_patterns or [])
        if sensitive and not reveal:
            display = redact_value(raw)
        elif len(raw) > max_value_length:
            display = raw[:max_value_length] + "..."
        else:
            display = raw
        entries.append(
            PreviewEntry(
                key=key,
                raw_value=raw,
                display_value=display,
                sensitive=sensitive,
                length=len(raw),
            )
        )
    return entries


def format_table(entries: List[PreviewEntry]) -> str:
    """Format preview entries as a plain-text table string."""
    if not entries:
        return "(no entries)"
    col_w = max(len(e.key) for e in entries) + 2
    lines = [f"{'KEY':<{col_w}}  {'VALUE'}", "-" * (col_w + 40)]
    for e in entries:
        flag = " [sensitive]" if e.sensitive else ""
        lines.append(f"{e.key:<{col_w}}  {e.display_value}{flag}")
    return "\n".join(lines)
