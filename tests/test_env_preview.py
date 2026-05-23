"""Tests for envault.env_preview."""
from __future__ import annotations

import pytest

from envault.env_preview import PreviewError, PreviewEntry, build_preview, format_table


SAMPLE: dict = {
    "API_KEY": "super_secret_123",
    "APP_NAME": "myapp",
    "DATABASE_PASSWORD": "hunter2",
    "PORT": "8080",
}


def test_build_preview_returns_sorted_entries():
    entries = build_preview(SAMPLE)
    keys = [e.key for e in entries]
    assert keys == sorted(keys)


def test_sensitive_key_is_redacted_by_default():
    entries = build_preview({"API_KEY": "mysecret"})
    assert entries[0].sensitive is True
    assert entries[0].display_value != "mysecret"


def test_sensitive_key_revealed_when_flag_set():
    entries = build_preview({"API_KEY": "mysecret"}, reveal=True)
    assert entries[0].display_value == "mysecret"


def test_non_sensitive_key_shown_plainly():
    entries = build_preview({"APP_NAME": "myapp"})
    assert entries[0].sensitive is False
    assert entries[0].display_value == "myapp"


def test_long_value_truncated():
    long_val = "x" * 100
    entries = build_preview({"SOME_VAR": long_val}, max_value_length=20)
    assert entries[0].display_value.endswith("...")
    assert len(entries[0].display_value) == 23  # 20 + "..."


def test_short_value_not_truncated():
    entries = build_preview({"KEY": "short"}, max_value_length=20)
    assert entries[0].display_value == "short"


def test_length_field_reflects_raw_value():
    entries = build_preview({"TOKEN": "abc"})
    assert entries[0].length == 3


def test_extra_patterns_mark_additional_keys_sensitive():
    entries = build_preview({"MY_CUSTOM": "val"}, extra_patterns=["MY_*"])
    assert entries[0].sensitive is True


def test_build_preview_raises_on_non_dict():
    with pytest.raises(PreviewError):
        build_preview(["not", "a", "dict"])  # type: ignore[arg-type]


def test_to_dict_contains_expected_keys():
    entries = build_preview({"PORT": "8080"})
    d = entries[0].to_dict()
    assert set(d.keys()) == {"key", "display_value", "sensitive", "length"}


def test_format_table_empty():
    assert format_table([]) == "(no entries)"


def test_format_table_contains_key_names():
    entries = build_preview({"PORT": "8080", "HOST": "localhost"})
    table = format_table(entries)
    assert "PORT" in table
    assert "HOST" in table


def test_format_table_marks_sensitive_entries():
    entries = build_preview({"API_KEY": "secret"})
    table = format_table(entries)
    assert "[sensitive]" in table


def test_format_table_no_sensitive_marker_for_plain_key():
    entries = build_preview({"APP_ENV": "production"})
    table = format_table(entries)
    assert "[sensitive]" not in table
