"""Integration helpers: operate on vault entries filtered by group."""
from __future__ import annotations
import click
from pathlib import Path
from envault.vault import Vault
from envault.env_group import get_group, GroupError


@click.group("group-ops")
def group_ops_group():
    """Bulk vault operations scoped to a named group."""


@group_ops_group.command("export")
@click.argument("vault_file")
@click.argument("password")
@click.argument("group_name")
def group_export(vault_file, password, group_name):
    """Print KEY=VALUE pairs for all keys in a group."""
    vp = Path(vault_file)
    keys = get_group(vp, group_name)
    if keys is None:
        click.echo(f"Group '{group_name}' not found.", err=True)
        raise SystemExit(1)
    vault = Vault(vp, password)
    missing = []
    for key in keys:
        value = vault.get(key)
        if value is None:
            missing.append(key)
        else:
            click.echo(f"{key}={value}")
    if missing:
        click.echo(f"Warning: keys not in vault: {', '.join(missing)}", err=True)


@group_ops_group.command("delete")
@click.argument("vault_file")
@click.argument("password")
@click.argument("group_name")
@click.option("--yes", is_flag=True, help="Skip confirmation.")
def group_delete(vault_file, password, group_name, yes):
    """Delete all vault entries belonging to a group."""
    vp = Path(vault_file)
    keys = get_group(vp, group_name)
    if keys is None:
        click.echo(f"Group '{group_name}' not found.", err=True)
        raise SystemExit(1)
    if not yes:
        click.confirm(
            f"Delete {len(keys)} key(s) from vault for group '{group_name}'?",
            abort=True,
        )
    vault = Vault(vp, password)
    removed = [k for k in keys if vault.delete(k)]
    click.echo(f"Deleted {len(removed)} key(s): {', '.join(removed) or 'none'}")
