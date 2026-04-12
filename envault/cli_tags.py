"""CLI commands for tagging vault entries."""

from __future__ import annotations

from pathlib import Path

import click

from envault.cli import get_vault
from envault.tags import TagStore


def _ts(vault_file: str) -> TagStore:
    tag_file = Path(vault_file).with_suffix(".tags.json")
    return TagStore(tag_file)


def _require_key(vault_file: str, key: str) -> None:
    """Raise ClickException if KEY does not exist in the vault."""
    vault = get_vault(vault_file)
    if vault.get(key) is None:
        raise click.ClickException(f"Key '{key}' not found in vault.")


@click.group("tag")
def tag_group() -> None:
    """Manage tags on vault entries."""


@tag_group.command("add")
@click.option("--vault", "vault_file", required=True, help="Path to vault file.")
@click.argument("key")
@click.argument("tag")
def tag_add(vault_file: str, key: str, tag: str) -> None:
    """Add TAG to KEY."""
    _require_key(vault_file, key)
    ts = _ts(vault_file)
    if tag in ts.get(key):
        raise click.ClickException(f"Tag '{tag}' already exists on key '{key}'.")
    ts.add(key, tag)
    click.echo(f"Tagged '{key}' with '{tag}'.")


@tag_group.command("remove")
@click.option("--vault", "vault_file", required=True, help="Path to vault file.")
@click.argument("key")
@click.argument("tag")
def tag_remove(vault_file: str, key: str, tag: str) -> None:
    """Remove TAG from KEY."""
    removed = _ts(vault_file).remove(key, tag)
    if removed:
        click.echo(f"Removed tag '{tag}' from '{key}'.")
    else:
        raise click.ClickException(f"Tag '{tag}' not found on key '{key}'.")


@tag_group.command("list")
@click.option("--vault", "vault_file", required=True, help="Path to vault file.")
@click.argument("key")
def tag_list(vault_file: str, key: str) -> None:
    """List all tags for KEY."""
    _require_key(vault_file, key)
    tags = _ts(vault_file).get(key)
    if tags:
        for t in tags:
            click.echo(t)
    else:
        click.echo(f"No tags for '{key}'.")


@tag_group.command("find")
@click.option("--vault", "vault_file", required=True, help="Path to vault file.")
@click.argument("tag")
def tag_find(vault_file: str, tag: str) -> None:
    """Find all keys carrying TAG."""
    keys = _ts(vault_file).keys_for_tag(tag)
    if keys:
        for k in keys:
            click.echo(k)
    else:
        click.echo(f"No keys found with tag '{tag}'.")


@tag_group.command("all")
@click.option("--vault", "vault_file", required=True, help="Path to vault file.")
def tag_all(vault_file: str) -> None:
    """List every tag used in the vault."""
    tags = _ts(vault_file).all_tags()
    if tags:
        for t in tags:
            click.echo(t)
    else:
        click.echo("No tags defined.")
