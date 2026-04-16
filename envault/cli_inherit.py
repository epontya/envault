"""CLI commands for vault inheritance."""
from __future__ import annotations

from pathlib import Path

import click

from envault.cli import get_vault
from envault.env_inherit import (
    InheritError,
    add_parent,
    list_parents,
    remove_parent,
    resolve_inherited,
)


@click.group("inherit")
def inherit_group() -> None:
    """Manage vault inheritance chains."""


@inherit_group.command("add")
@click.argument("parent_vault")
@click.option("--vault", "vault_file", required=True, type=click.Path())
@click.option("--password", prompt=True, hide_input=True)
def inherit_add(parent_vault: str, vault_file: str, password: str) -> None:
    """Register PARENT_VAULT as a parent of the current vault."""
    vp = Path(vault_file)
    get_vault(vp, password)  # validate credentials
    try:
        parents = add_parent(vp, parent_vault)
        click.echo(f"Added parent. Chain: {parents}")
    except InheritError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@inherit_group.command("remove")
@click.argument("parent_vault")
@click.option("--vault", "vault_file", required=True, type=click.Path())
@click.option("--password", prompt=True, hide_input=True)
def inherit_remove(parent_vault: str, vault_file: str, password: str) -> None:
    """Remove PARENT_VAULT from the inheritance chain."""
    vp = Path(vault_file)
    get_vault(vp, password)
    if remove_parent(vp, parent_vault):
        click.echo("Parent removed.")
    else:
        click.echo("Parent not found.", err=True)
        raise SystemExit(1)


@inherit_group.command("list")
@click.option("--vault", "vault_file", required=True, type=click.Path())
@click.option("--password", prompt=True, hide_input=True)
def inherit_list(vault_file: str, password: str) -> None:
    """List all parent vaults in the inheritance chain."""
    vp = Path(vault_file)
    get_vault(vp, password)
    parents = list_parents(vp)
    if not parents:
        click.echo("No parents configured.")
    else:
        for p in parents:
            click.echo(p)


@inherit_group.command("resolve")
@click.option("--vault", "vault_file", required=True, type=click.Path())
@click.option("--password", prompt=True, hide_input=True)
def inherit_resolve(vault_file: str, password: str) -> None:
    """Show the fully resolved env dict including inherited keys."""
    vp = Path(vault_file)
    try:
        merged = resolve_inherited(vp, password)
    except InheritError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
    for k, v in sorted(merged.items()):
        click.echo(f"{k}={v}")
