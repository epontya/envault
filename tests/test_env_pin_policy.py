"""Tests for envault.env_pin_policy."""
from __future__ import annotations

import pytest
from pathlib import Path

from envault.env_pin_policy import (
    PinPolicyError,
    enforce_policy,
    get_policy,
    remove_policy,
    set_policy,
    _policy_path,
)


@pytest.fixture()
def vpath(tmp_path: Path) -> Path:
    return tmp_path / "test.vault"


def test_set_policy_creates_file(vpath: Path) -> None:
    set_policy(vpath)
    assert _policy_path(vpath).exists()


def test_set_policy_returns_dict(vpath: Path) -> None:
    policy = set_policy(vpath, require_pin=True, min_pin_length=6, max_attempts=5)
    assert policy["require_pin"] is True
    assert policy["min_pin_length"] == 6
    assert policy["max_attempts"] == 5


def test_get_policy_defaults_when_no_file(vpath: Path) -> None:
    policy = get_policy(vpath)
    assert policy["require_pin"] is False
    assert policy["min_pin_length"] == 4
    assert policy["max_attempts"] == 3


def test_get_policy_reflects_saved_values(vpath: Path) -> None:
    set_policy(vpath, require_pin=True, min_pin_length=8, max_attempts=2)
    policy = get_policy(vpath)
    assert policy["require_pin"] is True
    assert policy["min_pin_length"] == 8
    assert policy["max_attempts"] == 2


def test_set_policy_min_length_below_4_raises(vpath: Path) -> None:
    with pytest.raises(PinPolicyError, match="min_pin_length"):
        set_policy(vpath, min_pin_length=3)


def test_set_policy_max_attempts_zero_raises(vpath: Path) -> None:
    with pytest.raises(PinPolicyError, match="max_attempts"):
        set_policy(vpath, max_attempts=0)


def test_remove_policy_returns_true_when_existed(vpath: Path) -> None:
    set_policy(vpath)
    assert remove_policy(vpath) is True


def test_remove_policy_returns_false_when_not_existed(vpath: Path) -> None:
    assert remove_policy(vpath) is False


def test_remove_policy_deletes_file(vpath: Path) -> None:
    set_policy(vpath)
    remove_policy(vpath)
    assert not _policy_path(vpath).exists()


def test_enforce_policy_passes_when_not_required(vpath: Path) -> None:
    set_policy(vpath, require_pin=False)
    enforce_policy(vpath, "x")  # should not raise


def test_enforce_policy_passes_with_valid_pin(vpath: Path) -> None:
    set_policy(vpath, require_pin=True, min_pin_length=4)
    enforce_policy(vpath, "1234")  # should not raise


def test_enforce_policy_raises_when_pin_too_short(vpath: Path) -> None:
    set_policy(vpath, require_pin=True, min_pin_length=6)
    with pytest.raises(PinPolicyError, match="at least 6"):
        enforce_policy(vpath, "123")


def test_enforce_policy_no_file_does_not_raise(vpath: Path) -> None:
    # Default policy has require_pin=False, so no error
    enforce_policy(vpath, "")
