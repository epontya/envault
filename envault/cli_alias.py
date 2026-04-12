"""CLI commands for managing key aliases."""

from __future__ import annotations

from pathlib import Path

import click

from envault.alias import AliasError, AliasStore
from envault.cli import get_vault


def _store(vault_path: str) -> AliasStore:
    alias_file = Path(vault_path).with_suffix(".aliases.json")
    return AliasStore(alias_file)


@click.group("alias")
def alias_group() -> None:
    """Manage short-hand aliases for vault keys."""


@alias_group.command("add")
@click.argument("alias")
@click.argument("key")
@click.option("--vault", "vault_path", envvar="ENVAULT_VAULT", required=True)
def alias_add(alias: str, key: str, vault_path: str) -> None:
    """Create ALIAS pointing to KEY."""
    vault = get_vault(vault_path)
    if vault.get(key) is None:
        click.echo(f"Warning: key {key!r} does not exist in the vault.", err=True)
    try:
        _store(vault_path).add(alias, key)
        click.echo(f"Alias '{alias}' -> '{key}' added.")
    except AliasError as exc:
        raise click.ClickException(str(exc)) from exc


@alias_group.command("remove")
@click.argument("alias")
@click.option("--vault", "vault_path", envvar="ENVAULT_VAULT", required=True)
def alias_remove(alias: str, vault_path: str) -> None:
    """Remove ALIAS."""
    removed = _store(vault_path).remove(alias)
    if removed:
        click.echo(f"Alias '{alias}' removed.")
    else:
        raise click.ClickException(f"Alias '{alias}' not found.")


@alias_group.command("list")
@click.option("--vault", "vault_path", envvar="ENVAULT_VAULT", required=True)
def alias_list(vault_path: str) -> None:
    """List all aliases."""
    entries = _store(vault_path).list_aliases()
    if not entries:
        click.echo("No aliases defined.")
        return
    width = max(len(a) for a, _ in entries)
    for alias, key in entries:
        click.echo(f"  {alias:<{width}}  ->  {key}")


@alias_group.command("resolve")
@click.argument("alias")
@click.option("--vault", "vault_path", envvar="ENVAULT_VAULT", required=True)
def alias_resolve(alias: str, vault_path: str) -> None:
    """Print the vault key that ALIAS points to."""
    key = _store(vault_path).resolve(alias)
    if key is None:
        raise click.ClickException(f"Alias '{alias}' not found.")
    click.echo(key)
