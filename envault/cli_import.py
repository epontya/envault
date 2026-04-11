"""CLI commands for importing environment variables into a vault."""

from __future__ import annotations

from pathlib import Path

import click

from envault.cli import get_vault
from envault.import_env import ImportError, import_from_dotenv, import_from_env, import_from_json


@click.group("import")
def import_group() -> None:
    """Import variables into the vault from external sources."""


@import_group.command("dotenv")
@click.argument("file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--overwrite/--no-overwrite", default=False, show_default=True,
              help="Overwrite existing keys.")
@click.pass_context
def import_dotenv(ctx: click.Context, file: Path, overwrite: bool) -> None:
    """Import variables from a .env FILE into the vault."""
    vault = get_vault(ctx)
    try:
        entries = import_from_dotenv(file)
    except ImportError as exc:
        raise click.ClickException(str(exc)) from exc
    imported, skipped = _write_entries(vault, entries, overwrite)
    click.echo(f"Imported {imported} variable(s), skipped {skipped} existing.")


@import_group.command("json")
@click.argument("file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--overwrite/--no-overwrite", default=False, show_default=True,
              help="Overwrite existing keys.")
@click.pass_context
def import_json(ctx: click.Context, file: Path, overwrite: bool) -> None:
    """Import variables from a JSON FILE into the vault."""
    vault = get_vault(ctx)
    try:
        entries = import_from_json(file)
    except ImportError as exc:
        raise click.ClickException(str(exc)) from exc
    imported, skipped = _write_entries(vault, entries, overwrite)
    click.echo(f"Imported {imported} variable(s), skipped {skipped} existing.")


@import_group.command("env")
@click.option("--prefix", default="", show_default=True,
              help="Only import variables whose names start with PREFIX.")
@click.option("--overwrite/--no-overwrite", default=False, show_default=True,
              help="Overwrite existing keys.")
@click.pass_context
def import_env(ctx: click.Context, prefix: str, overwrite: bool) -> None:
    """Import variables from the current environment into the vault."""
    vault = get_vault(ctx)
    entries = import_from_env(prefix)
    imported, skipped = _write_entries(vault, entries, overwrite)
    click.echo(f"Imported {imported} variable(s), skipped {skipped} existing.")


def _write_entries(vault, entries: dict, overwrite: bool) -> tuple[int, int]:
    imported = skipped = 0
    for key, value in entries.items():
        if not overwrite and vault.get(key) is not None:
            skipped += 1
            continue
        vault.set(key, value)
        imported += 1
    return imported, skipped
