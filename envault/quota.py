"""Quota management: enforce per-vault limits on number of entries and total value size."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


class QuotaError(Exception):
    """Raised when a quota constraint is violated."""


class QuotaConfig:
    """Stores and checks quota settings for a vault."""

    DEFAULT_MAX_ENTRIES: int = 500
    DEFAULT_MAX_VALUE_BYTES: int = 10 * 1024  # 10 KB per value
    DEFAULT_MAX_TOTAL_BYTES: int = 1024 * 1024  # 1 MB total

    def __init__(self, path: Path) -> None:
        self._path = path
        self._data: dict = self._load()

    def _load(self) -> dict:
        if self._path.exists():
            return json.loads(self._path.read_text())
        return {}

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._data, indent=2))

    def set_limit(self, max_entries: Optional[int] = None,
                  max_value_bytes: Optional[int] = None,
                  max_total_bytes: Optional[int] = None) -> None:
        if max_entries is not None:
            if max_entries < 1:
                raise QuotaError("max_entries must be >= 1")
            self._data["max_entries"] = max_entries
        if max_value_bytes is not None:
            if max_value_bytes < 1:
                raise QuotaError("max_value_bytes must be >= 1")
            self._data["max_value_bytes"] = max_value_bytes
        if max_total_bytes is not None:
            if max_total_bytes < 1:
                raise QuotaError("max_total_bytes must be >= 1")
            self._data["max_total_bytes"] = max_total_bytes
        self._save()

    def get_limits(self) -> dict:
        return {
            "max_entries": self._data.get("max_entries", self.DEFAULT_MAX_ENTRIES),
            "max_value_bytes": self._data.get("max_value_bytes", self.DEFAULT_MAX_VALUE_BYTES),
            "max_total_bytes": self._data.get("max_total_bytes", self.DEFAULT_MAX_TOTAL_BYTES),
        }

    def reset(self) -> None:
        self._data = {}
        self._save()


def check_quota(config: QuotaConfig, current_entries: dict[str, str],
                new_key: str, new_value: str) -> None:
    """Raise QuotaError if adding new_key/new_value would exceed any limit."""
    limits = config.get_limits()
    merged = {**current_entries, new_key: new_value}

    if len(merged) > limits["max_entries"]:
        raise QuotaError(
            f"Entry limit exceeded: max {limits['max_entries']} entries allowed."
        )

    value_bytes = len(new_value.encode())
    if value_bytes > limits["max_value_bytes"]:
        raise QuotaError(
            f"Value too large: {value_bytes} bytes exceeds limit of {limits['max_value_bytes']} bytes."
        )

    total_bytes = sum(len(v.encode()) for v in merged.values())
    if total_bytes > limits["max_total_bytes"]:
        raise QuotaError(
            f"Total size exceeded: {total_bytes} bytes exceeds limit of {limits['max_total_bytes']} bytes."
        )
