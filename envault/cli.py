"""Main CLI entry point for envault."""

from __future__ import annotations

import click
from pathlib import Path

from envault.vault import Vault, VaultNotFoundError


def get_vault(vault_file: str, password: str) -> Vault:
    """Return a Vault instance, creating the file if necessary."""
    return Vault(Path(vault_file), password)


@click.group()
def cli() -> None:
    """envault — secure environment variable manager."""


@cli.command("set")
@click.argument("key")
@click.argument("value")
@click.option("--vault-file", default="vault.db", show_default=True)
@click.password_option("--password", envvar="ENVAULT_PASSWORD", prompt="Vault password")
def set_cmd(key: str, value: str, vault_file: str, password: str) -> None:
    """Set a key/value pair in the vault."""
    vault = get_vault(vault_file, password)
    vault.set(key, value, password)
    click.echo(f"Set '{key}'.")


@cli.command("get")
@click.argument("key")
@click.option("--vault-file", default="vault.db", show_default=True)
@click.password_option("--password", envvar="ENVAULT_PASSWORD", prompt="Vault password")
def get_cmd(key: str, vault_file: str, password: str) -> None:
    """Get a value from the vault."""
    vault = get_vault(vault_file, password)
    value = vault.get(key, password)
    if value is None:
        raise click.ClickException(f"Key '{key}' not found.")
    click.echo(value)


@cli.command("delete")
@click.argument("key")
@click.option("--vault-file", default="vault.db", show_default=True)
@click.password_option("--password", envvar="ENVAULT_PASSWORD", prompt="Vault password")
def delete_cmd(key: str, vault_file: str, password: str) -> None:
    """Delete a key from the vault."""
    vault = get_vault(vault_file, password)
    deleted = vault.delete(key)
    if not deleted:
        raise click.ClickException(f"Key '{key}' not found.")
    click.echo(f"Deleted '{key}'.")


@cli.command("list")
@click.option("--vault-file", default="vault.db", show_default=True)
@click.password_option("--password", envvar="ENVAULT_PASSWORD", prompt="Vault password")
def list_cmd(vault_file: str, password: str) -> None:
    """List all keys in the vault."""
    vault = get_vault(vault_file, password)
    keys = vault.list_keys()
    if not keys:
        click.echo("No keys found.")
    else:
        for key in sorted(keys):
            click.echo(key)


# Register sub-command groups
from envault.cli_profiles import profile_group  # noqa: E402
from envault.cli_sync import sync_group  # noqa: E402
from envault.cli_audit import audit_group  # noqa: E402
from envault.cli_rotate import rotate_group  # noqa: E402
from envault.cli_snapshot import snapshot_group  # noqa: E402

cli.add_command(profile_group)
cli.add_command(sync_group)
cli.add_command(audit_group)
cli.add_command(rotate_group)
cli.add_command(snapshot_group)
