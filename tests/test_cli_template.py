"""Tests for envault.cli_template."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli import cli
from envault.cli_template import template_group
from envault.vault import Vault


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_file(tmp_path):
    path = str(tmp_path / "vault.db")
    v = Vault(path)
    v.set("GREETING", "Hello", "pass")
    v.set("NAME", "World", "pass")
    return path


def _invoke(runner, vault_file, *args):
    # Register template_group on the cli for testing
    if "template" not in [c.name for c in cli.commands.values()]:
        cli.add_command(template_group, "template")
    return runner.invoke(
        cli,
        ["template"] + list(args),
        catch_exceptions=False,
    )


def test_preview_renders_inline(runner, vault_file):
    result = runner.invoke(
        template_group,
        ["preview", "{{ GREETING }}, {{ NAME }}!", "--vault", vault_file, "--password", "pass"],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "Hello, World!" in result.output


def test_preview_missing_key_strict_exits_nonzero(runner, vault_file):
    result = runner.invoke(
        template_group,
        ["preview", "{{ MISSING }}", "--vault", vault_file, "--password", "pass", "--strict"],
    )
    assert result.exit_code != 0
    assert "MISSING" in result.output


def test_preview_missing_key_no_strict_leaves_placeholder(runner, vault_file):
    result = runner.invoke(
        template_group,
        ["preview", "{{ MISSING }}", "--vault", vault_file, "--password", "pass", "--no-strict"],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "{{ MISSING }}" in result.output


def test_render_file_to_stdout(runner, vault_file, tmp_path):
    tpl = tmp_path / "t.tpl"
    tpl.write_text("{{ GREETING }}, {{ NAME }}!\n")
    result = runner.invoke(
        template_group,
        ["render", str(tpl), "--vault", vault_file, "--password", "pass"],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "Hello, World!" in result.output


def test_render_file_to_output_file(runner, vault_file, tmp_path):
    tpl = tmp_path / "t.tpl"
    tpl.write_text("{{ GREETING }}")
    out = tmp_path / "out.txt"
    result = runner.invoke(
        template_group,
        ["render", str(tpl), "--vault", vault_file, "--password", "pass", "--output", str(out)],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert out.read_text() == "Hello"
