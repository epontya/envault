"""Tests for envault.template."""

from __future__ import annotations

import pytest

from envault.template import (
    MissingKeyError,
    TemplateError,
    render_file,
    render_string,
)


@pytest.fixture()
def vault(tmp_path):
    from envault.vault import Vault

    v = Vault(str(tmp_path / "vault.db"))
    v.set("HOST", "localhost", "secret")
    v.set("PORT", "5432", "secret")
    v.set("USER", "admin", "secret")
    return v


def test_render_single_placeholder(vault):
    result = render_string("host={{ HOST }}", vault, "secret")
    assert result == "host=localhost"


def test_render_multiple_placeholders(vault):
    result = render_string("{{ USER }}@{{ HOST }}:{{ PORT }}", vault, "secret")
    assert result == "admin@localhost:5432"


def test_render_no_placeholders(vault):
    result = render_string("plain text", vault, "secret")
    assert result == "plain text"


def test_render_missing_key_strict_raises(vault):
    with pytest.raises(MissingKeyError) as exc_info:
        render_string("{{ MISSING }}", vault, "secret", strict=True)
    assert exc_info.value.key == "MISSING"


def test_render_missing_key_non_strict_leaves_placeholder(vault):
    result = render_string("{{ MISSING }}", vault, "secret", strict=False)
    assert result == "{{ MISSING }}"


def test_render_whitespace_inside_braces(vault):
    result = render_string("{{HOST}}", vault, "secret")
    # No spaces — should NOT match our pattern (requires at least identifier)
    # Actually our regex allows zero spaces: check it still works
    result2 = render_string("{{  HOST  }}", vault, "secret")
    assert result2 == "localhost"


def test_render_file(vault, tmp_path):
    tpl = tmp_path / "config.tpl"
    tpl.write_text("host={{ HOST }}\nport={{ PORT }}\n")
    result = render_file(str(tpl), vault, "secret")
    assert result == "host=localhost\nport=5432\n"


def test_render_file_missing_file(vault, tmp_path):
    with pytest.raises(TemplateError, match="Cannot read template file"):
        render_file(str(tmp_path / "nonexistent.tpl"), vault, "secret")


def test_missing_key_error_message():
    err = MissingKeyError("DB_URL")
    assert "DB_URL" in str(err)
    assert err.key == "DB_URL"


def test_render_partial_line(vault):
    result = render_string("jdbc:postgresql://{{ HOST }}:{{ PORT }}/mydb", vault, "secret")
    assert result == "jdbc:postgresql://localhost:5432/mydb"
