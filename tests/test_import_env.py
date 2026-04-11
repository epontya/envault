"""Tests for envault.import_env."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from envault.import_env import ImportError, import_from_dotenv, import_from_env, import_from_json


# ---------------------------------------------------------------------------
# import_from_dotenv
# ---------------------------------------------------------------------------

def test_dotenv_simple(tmp_path: Path) -> None:
    f = tmp_path / ".env"
    f.write_text("FOO=bar\nBAZ=qux\n")
    assert import_from_dotenv(f) == {"FOO": "bar", "BAZ": "qux"}


def test_dotenv_strips_double_quotes(tmp_path: Path) -> None:
    f = tmp_path / ".env"
    f.write_text('KEY="hello world"\n')
    assert import_from_dotenv(f)["KEY"] == "hello world"


def test_dotenv_strips_single_quotes(tmp_path: Path) -> None:
    f = tmp_path / ".env"
    f.write_text("KEY='hello world'\n")
    assert import_from_dotenv(f)["KEY"] == "hello world"


def test_dotenv_ignores_comments(tmp_path: Path) -> None:
    f = tmp_path / ".env"
    f.write_text("# comment\nFOO=1\n")
    assert "#" not in import_from_dotenv(f)
    assert import_from_dotenv(f)["FOO"] == "1"


def test_dotenv_ignores_blank_lines(tmp_path: Path) -> None:
    f = tmp_path / ".env"
    f.write_text("\nFOO=bar\n\n")
    assert import_from_dotenv(f) == {"FOO": "bar"}


def test_dotenv_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(ImportError, match="not found"):
        import_from_dotenv(tmp_path / "missing.env")


# ---------------------------------------------------------------------------
# import_from_json
# ---------------------------------------------------------------------------

def test_json_simple(tmp_path: Path) -> None:
    f = tmp_path / "vars.json"
    f.write_text(json.dumps({"A": "1", "B": "2"}))
    assert import_from_json(f) == {"A": "1", "B": "2"}


def test_json_coerces_numbers(tmp_path: Path) -> None:
    f = tmp_path / "vars.json"
    f.write_text(json.dumps({"PORT": 8080}))
    assert import_from_json(f)["PORT"] == "8080"


def test_json_invalid_raises(tmp_path: Path) -> None:
    f = tmp_path / "vars.json"
    f.write_text("not json")
    with pytest.raises(ImportError, match="Invalid JSON"):
        import_from_json(f)


def test_json_non_dict_raises(tmp_path: Path) -> None:
    f = tmp_path / "vars.json"
    f.write_text(json.dumps(["a", "b"]))
    with pytest.raises(ImportError, match="object"):
        import_from_json(f)


def test_json_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(ImportError, match="not found"):
        import_from_json(Path("/nonexistent/vars.json"))


# ---------------------------------------------------------------------------
# import_from_env
# ---------------------------------------------------------------------------

def test_import_env_no_prefix(monkeypatch) -> None:
    monkeypatch.setenv("MY_VAR", "hello")
    result = import_from_env()
    assert "MY_VAR" in result
    assert result["MY_VAR"] == "hello"


def test_import_env_with_prefix(monkeypatch) -> None:
    monkeypatch.setenv("APP_SECRET", "s3cr3t")
    monkeypatch.setenv("OTHER_VAR", "ignore")
    result = import_from_env(prefix="APP_")
    assert "APP_SECRET" in result
    assert "OTHER_VAR" not in result


def test_import_env_empty_prefix_returns_all(monkeypatch) -> None:
    monkeypatch.setenv("UNIQUE_XYZ_123", "yes")
    result = import_from_env(prefix="")
    assert "UNIQUE_XYZ_123" in result
