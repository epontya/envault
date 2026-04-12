"""Tests for envault.quota."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.quota import QuotaConfig, QuotaError, check_quota


@pytest.fixture
def cfg(tmp_path: Path) -> QuotaConfig:
    return QuotaConfig(tmp_path / "vault.quota.json")


def test_default_limits(cfg: QuotaConfig) -> None:
    limits = cfg.get_limits()
    assert limits["max_entries"] == QuotaConfig.DEFAULT_MAX_ENTRIES
    assert limits["max_value_bytes"] == QuotaConfig.DEFAULT_MAX_VALUE_BYTES
    assert limits["max_total_bytes"] == QuotaConfig.DEFAULT_MAX_TOTAL_BYTES


def test_set_max_entries(cfg: QuotaConfig) -> None:
    cfg.set_limit(max_entries=10)
    assert cfg.get_limits()["max_entries"] == 10


def test_set_max_value_bytes(cfg: QuotaConfig) -> None:
    cfg.set_limit(max_value_bytes=256)
    assert cfg.get_limits()["max_value_bytes"] == 256


def test_set_max_total_bytes(cfg: QuotaConfig) -> None:
    cfg.set_limit(max_total_bytes=2048)
    assert cfg.get_limits()["max_total_bytes"] == 2048


def test_set_invalid_max_entries_raises(cfg: QuotaConfig) -> None:
    with pytest.raises(QuotaError):
        cfg.set_limit(max_entries=0)


def test_set_invalid_max_value_bytes_raises(cfg: QuotaConfig) -> None:
    with pytest.raises(QuotaError):
        cfg.set_limit(max_value_bytes=-1)


def test_reset_restores_defaults(cfg: QuotaConfig) -> None:
    cfg.set_limit(max_entries=5)
    cfg.reset()
    assert cfg.get_limits()["max_entries"] == QuotaConfig.DEFAULT_MAX_ENTRIES


def test_limits_persisted(tmp_path: Path) -> None:
    path = tmp_path / "vault.quota.json"
    cfg1 = QuotaConfig(path)
    cfg1.set_limit(max_entries=7)
    cfg2 = QuotaConfig(path)
    assert cfg2.get_limits()["max_entries"] == 7


def test_check_quota_passes(cfg: QuotaConfig) -> None:
    cfg.set_limit(max_entries=5)
    check_quota(cfg, {"A": "1", "B": "2"}, "C", "3")  # no error


def test_check_quota_entry_limit_exceeded(cfg: QuotaConfig) -> None:
    cfg.set_limit(max_entries=2)
    with pytest.raises(QuotaError, match="Entry limit"):
        check_quota(cfg, {"A": "1", "B": "2"}, "C", "3")


def test_check_quota_value_too_large(cfg: QuotaConfig) -> None:
    cfg.set_limit(max_value_bytes=5)
    with pytest.raises(QuotaError, match="Value too large"):
        check_quota(cfg, {}, "KEY", "toolongvalue")


def test_check_quota_total_exceeded(cfg: QuotaConfig) -> None:
    cfg.set_limit(max_total_bytes=10)
    existing = {"A": "12345678"}
    with pytest.raises(QuotaError, match="Total size"):
        check_quota(cfg, existing, "B", "123")


def test_check_quota_update_existing_key_no_double_count(cfg: QuotaConfig) -> None:
    cfg.set_limit(max_total_bytes=20)
    existing = {"A": "12345678901234567890"}  # 20 bytes exactly
    # Updating the same key should not double-count
    check_quota(cfg, existing, "A", "short")  # no error
