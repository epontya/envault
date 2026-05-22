"""Tests for envault.env_mask."""
from __future__ import annotations

import pytest

from envault.env_mask import (
    DEFAULT_MASK,
    MaskError,
    is_sensitive_key,
    mask_dict,
    mask_value,
)


# ---------------------------------------------------------------------------
# is_sensitive_key
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("key", [
    "password", "PASSWORD", "db_password",
    "secret", "MY_SECRET",
    "token", "AUTH_TOKEN",
    "api_key", "API-KEY", "APIKEY",
    "auth", "AUTH_HEADER",
    "credential", "CREDENTIALS",
    "private_key", "PRIVATE-KEY",
    "access_key", "AWS_ACCESS_KEY",
])
def test_sensitive_keys(key: str) -> None:
    assert is_sensitive_key(key) is True


@pytest.mark.parametrize("key", [
    "username", "host", "port", "DATABASE_URL", "REGION", "LOG_LEVEL",
])
def test_non_sensitive_keys(key: str) -> None:
    assert is_sensitive_key(key) is False


def test_extra_patterns_extend_detection() -> None:
    assert is_sensitive_key("MY_PIN", extra_patterns=[r"pin"]) is True


def test_extra_patterns_do_not_affect_non_matching() -> None:
    assert is_sensitive_key("LOG_LEVEL", extra_patterns=[r"pin"]) is False


# ---------------------------------------------------------------------------
# mask_value
# ---------------------------------------------------------------------------

def test_mask_value_default() -> None:
    assert mask_value("supersecret") == DEFAULT_MASK


def test_mask_value_reveal_chars() -> None:
    result = mask_value("supersecret", reveal_chars=3)
    assert result.endswith("ret")
    assert result.startswith(DEFAULT_MASK)


def test_mask_value_reveal_chars_gte_length_returns_full_mask() -> None:
    assert mask_value("abc", reveal_chars=10) == DEFAULT_MASK


def test_mask_value_custom_mask() -> None:
    assert mask_value("value", mask="[HIDDEN]") == "[HIDDEN]"


def test_mask_value_non_string_raises() -> None:
    with pytest.raises(MaskError):
        mask_value(123)  # type: ignore[arg-type]


def test_mask_value_negative_reveal_raises() -> None:
    with pytest.raises(MaskError):
        mask_value("value", reveal_chars=-1)


# ---------------------------------------------------------------------------
# mask_dict
# ---------------------------------------------------------------------------

def test_mask_dict_masks_sensitive_keys() -> None:
    data = {"password": "s3cr3t", "host": "localhost"}
    result = mask_dict(data)
    assert result["password"] == DEFAULT_MASK
    assert result["host"] == "localhost"


def test_mask_dict_does_not_mutate_original() -> None:
    data = {"password": "s3cr3t"}
    mask_dict(data)
    assert data["password"] == "s3cr3t"


def test_mask_dict_empty_returns_empty() -> None:
    assert mask_dict({}) == {}


def test_mask_dict_reveal_chars_propagated() -> None:
    data = {"api_key": "abcdef"}
    result = mask_dict(data, reveal_chars=2)
    assert result["api_key"].endswith("ef")


def test_mask_dict_extra_patterns() -> None:
    data = {"MY_PIN": "1234", "host": "localhost"}
    result = mask_dict(data, extra_patterns=[r"pin"])
    assert result["MY_PIN"] == DEFAULT_MASK
    assert result["host"] == "localhost"
