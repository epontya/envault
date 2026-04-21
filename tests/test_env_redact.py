"""Tests for envault.env_redact."""

import re
import pytest

from envault.env_redact import (
    DEFAULT_MASK,
    RedactError,
    is_sensitive_key,
    redact_dict,
    redact_value,
)


# ---------------------------------------------------------------------------
# is_sensitive_key
# ---------------------------------------------------------------------------


def test_sensitive_key_password():
    assert is_sensitive_key("DB_PASSWORD") is True


def test_sensitive_key_token():
    assert is_sensitive_key("GITHUB_TOKEN") is True


def test_sensitive_key_api_key():
    assert is_sensitive_key("STRIPE_API_KEY") is True


def test_non_sensitive_key():
    assert is_sensitive_key("APP_NAME") is False


def test_sensitive_key_custom_pattern():
    patterns = [re.compile(r"custom", re.IGNORECASE)]
    assert is_sensitive_key("MY_CUSTOM_VAR", patterns=patterns) is True
    assert is_sensitive_key("APP_NAME", patterns=patterns) is False


# ---------------------------------------------------------------------------
# redact_value
# ---------------------------------------------------------------------------


def test_redact_value_full_mask():
    assert redact_value("supersecret") == DEFAULT_MASK


def test_redact_value_with_visible_chars():
    result = redact_value("supersecret", visible_chars=3)
    assert result == DEFAULT_MASK + "ret"


def test_redact_value_visible_chars_exceeds_length():
    # When visible_chars >= len(value), still return full mask
    assert redact_value("abc", visible_chars=10) == DEFAULT_MASK


def test_redact_value_empty_string():
    assert redact_value("") == DEFAULT_MASK


def test_redact_value_custom_mask():
    assert redact_value("secret", mask="[HIDDEN]") == "[HIDDEN]"


def test_redact_value_negative_visible_chars_raises():
    with pytest.raises(RedactError):
        redact_value("secret", visible_chars=-1)


# ---------------------------------------------------------------------------
# redact_dict
# ---------------------------------------------------------------------------


def test_redact_dict_masks_sensitive_keys():
    data = {"DB_PASSWORD": "hunter2", "APP_NAME": "myapp"}
    result = redact_dict(data)
    assert result["DB_PASSWORD"] == DEFAULT_MASK
    assert result["APP_NAME"] == "myapp"


def test_redact_dict_explicit_keys():
    data = {"CUSTOM_VAR": "value123", "OTHER": "visible"}
    result = redact_dict(data, keys=["CUSTOM_VAR"])
    assert result["CUSTOM_VAR"] == DEFAULT_MASK
    assert result["OTHER"] == "visible"


def test_redact_dict_does_not_mutate_original():
    data = {"DB_PASSWORD": "secret"}
    redact_dict(data)
    assert data["DB_PASSWORD"] == "secret"


def test_redact_dict_empty_data():
    assert redact_dict({}) == {}


def test_redact_dict_with_visible_chars():
    data = {"API_KEY": "abcdef1234"}
    result = redact_dict(data, visible_chars=4)
    assert result["API_KEY"] == DEFAULT_MASK + "1234"
