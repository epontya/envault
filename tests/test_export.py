"""Tests for envault.export."""

import json

import pytest

from envault.export import export_secrets, SUPPORTED_FORMATS


SAMPLE: dict[str, str] = {
    "DATABASE_URL": "postgres://user:pass@localhost/db",
    "SECRET_KEY": "s3cr3t!",
    "PORT": "8080",
}


# ---------------------------------------------------------------------------
# dotenv format
# ---------------------------------------------------------------------------

def test_dotenv_simple_values():
    out = export_secrets({"PORT": "8080"}, fmt="dotenv")
    assert "PORT=8080" in out


def test_dotenv_quotes_values_with_spaces():
    out = export_secrets({"MSG": "hello world"}, fmt="dotenv")
    assert 'MSG="hello world"' in out


def test_dotenv_escapes_double_quotes():
    out = export_secrets({"GREETING": 'say "hi"'}, fmt="dotenv")
    assert '\\"' in out


def test_dotenv_ends_with_newline():
    out = export_secrets(SAMPLE, fmt="dotenv")
    assert out.endswith("\n")


def test_dotenv_empty_dict():
    assert export_secrets({}, fmt="dotenv") == ""


def test_dotenv_sorted_keys():
    out = export_secrets({"Z": "z", "A": "a"}, fmt="dotenv")
    assert out.index("A=") < out.index("Z=")


# ---------------------------------------------------------------------------
# shell format
# ---------------------------------------------------------------------------

def test_shell_contains_export():
    out = export_secrets({"FOO": "bar"}, fmt="shell")
    assert out.startswith("export FOO=\"bar\"")


def test_shell_ends_with_newline():
    out = export_secrets(SAMPLE, fmt="shell")
    assert out.endswith("\n")


def test_shell_empty_dict():
    assert export_secrets({}, fmt="shell") == ""


# ---------------------------------------------------------------------------
# json format
# ---------------------------------------------------------------------------

def test_json_is_valid():
    out = export_secrets(SAMPLE, fmt="json")
    parsed = json.loads(out)
    assert parsed == SAMPLE


def test_json_sorted_keys():
    out = export_secrets({"Z": "z", "A": "a"}, fmt="json")
    parsed = json.loads(out)
    assert list(parsed.keys()) == sorted(parsed.keys())


def test_json_ends_with_newline():
    out = export_secrets(SAMPLE, fmt="json")
    assert out.endswith("\n")


# ---------------------------------------------------------------------------
# unknown format
# ---------------------------------------------------------------------------

def test_unknown_format_raises():
    with pytest.raises(ValueError, match="Unknown format"):
        export_secrets(SAMPLE, fmt="xml")


def test_supported_formats_constant():
    assert "dotenv" in SUPPORTED_FORMATS
    assert "shell" in SUPPORTED_FORMATS
    assert "json" in SUPPORTED_FORMATS
