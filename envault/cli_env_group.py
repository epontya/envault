"""CLI commands for managing vault key groups."""
from __future__ import annotations
import click
from pathlib import Path
from envault.env_group import (
    GroupError, create_group, get_group, remove_group,
    list_groups, add_key_to_group, remove_key_from_group,
)


def _vp(vault_file: str) -> Path:
    return Path(vault_file)


@click.group("group")
def group_group():
    """Manage named key groups within a vault."""


@group_group.command("create")
@click.argument("vault_file")
@click.argument("group_name")
@click.argument("keys", nargs=-1, required=True)
def group_create(vault_file, group_name, keys):
    """Create a group with the specified keys."""
    try:
        result = create_group(_vp(vault_file), group_name, list(keys))
        click.echo(f"Group '{group_name}' created with keys: {', '.join(result)}")
    except GroupError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@group_group.command("get")
@click.argument("vault_file")
@click.argument("group_name")
def group_get(vault_file, group_name):
    """Show keys in a group."""
    keys = get_group(_vp(vault_file), group_name)
    if keys is None:
        click.echo(f"Group '{group_name}' not found.", err=True)
        raise SystemExit(1)
    for k in keys:
        click.echo(k)


@group_group.command("remove")
@click.argument("vault_file")
@click.argument("group_name")
def group_remove(vault_file, group_name):
    """Remove a group."""
    if not remove_group(_vp(vault_file), group_name):
        click.echo(f"Group '{group_name}' not found.", err=True)
        raise SystemExit(1)
    click.echo(f"Group '{group_name}' removed.")


@group_group.command("list")
@click.argument("vault_file")
def group_list(vault_file):
    """List all groups and their keys."""
    groups = list_groups(_vp(vault_file))
    if not groups:
        click.echo("No groups defined.")
        return
    for name, keys in sorted(groups.items()):
        click.echo(f"{name}: {', '.join(keys)}")


@group_group.command("add-key")
@click.argument("vault_file")
@click.argument("group_name")
@click.argument("key")
def group_add_key(vault_file, group_name, key):
    """Add a key to an existing group."""
    try:
        result = add_key_to_group(_vp(vault_file), group_name, key)
        click.echo(f"Key '{key}' added. Group '{group_name}': {', '.join(result)}")
    except GroupError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@group_group.command("remove-key")
@click.argument("vault_file")
@click.argument("group_name")
@click.argument("key")
def group_remove_key(vault_file, group_name, key):
    """Remove a key from a group."""
    if not remove_key_from_group(_vp(vault_file), group_name, key):
        click.echo(f"Key '{key}' not found in group '{group_name}'.", err=True)
        raise SystemExit(1)
    click.echo(f"Key '{key}' removed from group '{group_name}'.")
