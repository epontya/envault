"""Compute statistics and summary metrics for a vault's entries."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envault.vault import Vault, VaultNotFoundError


class StatsError(Exception):
    """Raised when stats cannot be computed."""


@dataclass
class VaultStats:
    total_keys: int = 0
    empty_values: int = 0
    avg_value_length: float = 0.0
    max_value_length: int = 0
    min_value_length: int = 0
    total_bytes: int = 0
    key_lengths: List[int] = field(default_factory=list)
    longest_key: str = ""
    shortest_key: str = ""

    def summary(self) -> str:
        lines = [
            f"Total keys       : {self.total_keys}",
            f"Empty values     : {self.empty_values}",
            f"Total bytes      : {self.total_bytes}",
            f"Avg value length : {self.avg_value_length:.1f}",
            f"Max value length : {self.max_value_length}",
            f"Min value length : {self.min_value_length}",
            f"Longest key      : {self.longest_key!r}",
            f"Shortest key     : {self.shortest_key!r}",
        ]
        return "\n".join(lines)


def compute_stats(vault: Vault) -> VaultStats:
    """Return a VaultStats object for *vault*."""
    entries: Dict[str, str] = vault.all()
    if not entries:
        return VaultStats()

    stats = VaultStats()
    stats.total_keys = len(entries)

    value_lengths: List[int] = []
    key_lengths: List[int] = []

    for k, v in entries.items():
        vlen = len(v)
        klen = len(k)
        value_lengths.append(vlen)
        key_lengths.append(klen)
        stats.total_bytes += klen + vlen
        if v == "":
            stats.empty_values += 1

    stats.avg_value_length = sum(value_lengths) / len(value_lengths)
    stats.max_value_length = max(value_lengths)
    stats.min_value_length = min(value_lengths)
    stats.key_lengths = key_lengths

    sorted_keys = sorted(entries.keys(), key=len)
    stats.shortest_key = sorted_keys[0]
    stats.longest_key = sorted_keys[-1]

    return stats
