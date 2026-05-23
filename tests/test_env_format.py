"""Tests for envault.env_format."""
import pytest

from envault.env_format import (
    FormatError,
    apply_format,
    format_as_bool,
    format_as_float,
    format_as_int,
    format_as_url,
    list_formats,
)


# ---------------------------------------------------------------------------
# list_formats
# ---------------------------------------------------------------------------

def test_list_formats_returns_known_names():
    names = list_formats()
    assert "bool" in names
    assert "int" in names
    assert "float" in names
    assert "url" in names


def test_list_formats_is_sorted():
    names = list_formats()
    assert names == sorted(names)


# ---------------------------------------------------------------------------
# format_as_bool
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("v", ["true", "True", "TRUE", "1", "yes", "on"])
def test_bool_true_variants(v):
    assert format_as_bool(v) == "true"


@pytest.mark.parametrize("v", ["false", "False", "FALSE", "0", "no", "off"])
def test_bool_false_variants(v):
    assert format_as_bool(v) == "false"


def test_bool_invalid_raises():
    with pytest.raises(FormatError):
        format_as_bool("maybe")


# ---------------------------------------------------------------------------
# format_as_int
# ---------------------------------------------------------------------------

def test_int_valid():
    assert format_as_int("42") == "42"


def test_int_strips_whitespace():
    assert format_as_int("  7  ") == "7"


def test_int_negative():
    assert format_as_int("-3") == "-3"


def test_int_invalid_raises():
    with pytest.raises(FormatError):
        format_as_int("3.14")


# ---------------------------------------------------------------------------
# format_as_float
# ---------------------------------------------------------------------------

def test_float_valid():
    assert format_as_float("3.14") == "3.14"


def test_float_integer_input():
    assert format_as_float("10") == "10.0"


def test_float_invalid_raises():
    with pytest.raises(FormatError):
        format_as_float("not-a-number")


# ---------------------------------------------------------------------------
# format_as_url
# ---------------------------------------------------------------------------

def test_url_lowercases_scheme_and_host():
    assert format_as_url("HTTPS://Example.COM/path") == "https://example.com/path"


def test_url_preserves_path_case():
    result = format_as_url("http://host.io/Path/To/Resource")
    assert result.endswith("/Path/To/Resource")


def test_url_no_path():
    assert format_as_url("https://api.example.com") == "https://api.example.com"


def test_url_invalid_raises():
    with pytest.raises(FormatError):
        format_as_url("not-a-url")


# ---------------------------------------------------------------------------
# apply_format
# ---------------------------------------------------------------------------

def test_apply_format_bool():
    assert apply_format("yes", "bool") == "true"


def test_apply_format_int():
    assert apply_format("99", "int") == "99"


def test_apply_format_unknown_raises():
    with pytest.raises(FormatError, match="Unknown format"):
        apply_format("value", "base64")


def test_apply_format_case_insensitive_name():
    assert apply_format("1", "BOOL") == "true"
