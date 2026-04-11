"""Core CLI entry point for envault."""

from __future__ import annotations

from pathlib import Path

import click

from envault.vault import Vault, VaultNotFoundError


def get_vault(vault_file: str, password: str | None = None) -> Vault:
    """Return a Vault instance, prompting for password when needed."""
    if password is None:
        password = click.prompt("Vault password", hide_input=True)
    return Vault(vault_file, password)


@click.group()
def cli() -> None:
    """envault — secure environment variable manager."""


@cli.command("set")
@click.option("--vault", "vault_file", required=True)
@click.option("--password", prompt=True, hide_input=True)
@click.argument("key")
@click.argument("value")
def set_cmd(vault_file: str, password: str, key: str, value: str) -> None:
    """Store a key/value pair in the vault."""
    vault = Vault(vault_file, password)
    vault.set(key, value)
    click.echo(f"Set '{key}'.")


@cli.command("get")
@click.option("--vault", "vault_file", required=True)
@click.option("--password", prompt=True, hide_input=True)
@click.argument("key")
def get_cmd(vault_file: str, password: str, key: str) -> None:
    """Retrieve a value from the vault."""
    try:
        vault = Vault(vault_file, password)
    except VaultNotFoundError as exc:
        raise click.ClickException(str(exc))
    value = vault.get(key)
    if value is None:
        raise click.ClickException(f"Key '{key}' not found.")
    click.echo(value)


@cli.command("delete")
@click.option("--vault", "vault_file", required=True)
@click.option("--password", prompt=True, hide_input=True)
@click.argument("key")
def delete_cmd(vault_file: str, password: str, key: str) -> None:
    """Delete a key from the vault."""
    try:
        vault = Vault(vault_file, password)
    except VaultNotFoundError as exc:
        raise click.ClickException(str(exc))
    deleted = vault.delete(key)
    if deleted:
        click.echo(f"Deleted '{key}'.")
    else:
        raise click.ClickException(f"Key '{key}' not found.")


@cli.command("list")
@click.option("--vault", "vault_file", required=True)
@click.option("--password", prompt=True, hide_input=True)
def list_cmd(vault_file: str, password: str) -> None:
    """List all keys in the vault."""
    try:
        vault = Vault(vault_file, password)
    except VaultNotFoundError as exc:
        raise click.ClickException(str(exc))
    keys = vault.keys()
    if keys:
        for k in sorted(keys):
            click.echo(k)
    else:
        click.echo("Vault is empty.")


# Register sub-command groups
from envault.cli_profiles import profile_group  # noqa: E402
from envault.cli_sync import sync_group  # noqa: E402
from envault.cli_audit import audit_group  # noqa: E402
from envault.cli_rotate import rotate_group  # noqa: E402
from envault.cli_snapshot import snapshot_group  # noqa: E402
from envault.cli_import import import_group  # noqa: E402
from envault.cli_copy import copy_group  # noqa: E402
from envault.cli_diff import diff_group  # noqa: E402
from envault.cli_tags import tag_group  # noqa: E402

cli.add_command(profile_group)
cli.add_command(sync_group)
cli.add_command(audit_group)
cli.add_command(rotate_group)
cli.add_command(snapshot_group)
cli.add_command(import_group)
cli.add_command(copy_group)
cli.add_command(diff_group)
cli.add_command(tag_group)
