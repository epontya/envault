"""Integration helpers: export resolved (inherited) env in various formats."""
from __future__ import annotations

from pathlib import Path

import click

from envault.env_inherit import InheritError, resolve_inherited
from envault.export import export_dotenv, export_json, export_shell


@click.group("inherit-export")
def inherit_export_group() -> None:
    """Export the fully resolved (inherited) environment."""


@inherit_export_group.command("dotenv")
@click.option("--vault", "vault_file", required=True, type=click.Path())
@click.option("--password", prompt=True, hide_input=True)
def ie_dotenv(vault_file: str, password: str) -> None:
    """Export resolved env as .env format."""
    _emit(vault_file, password, export_dotenv)


@inherit_export_group.command("shell")
@click.option("--vault", "vault_file", required=True, type=click.Path())
@click.option("--password", prompt=True, hide_input=True)
def ie_shell(vault_file: str, password: str) -> None:
    """Export resolved env as shell export statements."""
    _emit(vault_file, password, export_shell)


@inherit_export_group.command("json")
@click.option("--vault", "vault_file", required=True, type=click.Path())
@click.option("--password", prompt=True, hide_input=True)
def ie_json(vault_file: str, password: str) -> None:
    """Export resolved env as JSON."""
    _emit(vault_file, password, export_json)


def _emit(vault_file: str, password: str, formatter) -> None:
    vp = Path(vault_file)
    try:
        merged = resolve_inherited(vp, password)
    except InheritError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
    click.echo(formatter(merged), nl=False)
