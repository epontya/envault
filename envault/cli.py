"""Main CLI entry-point for envault."""

from __future__ import annotations

from pathlib import Path

import click

from envault.vault import Vault, VaultNotFoundError
from envault.cli_profiles import profile_group

DEFAULT_VAULT = Path.home() / ".envault" / "default.vault"


def get_vault(vault_path: Path, password: str) -> Vault:
    """Open an existing vault or create a new one."""
    return Vault(vault_path, password)


@click.group()
def cli() -> None:
    """envault — secure environment variable manager."""


cli.add_command(profile_group)


@cli.command("set")
@click.argument("key")
@click.argument("value")
@click.option("--vault", "vault_path", default=str(DEFAULT_VAULT), show_default=True, type=click.Path(path_type=Path))
@click.password_option("--password", envvar="ENVAULT_PASSWORD", prompt=True)
def set_cmd(key: str, value: str, vault_path: Path, password: str) -> None:
    """Set KEY to VALUE in the vault."""
    vault = get_vault(vault_path, password)
    vault.set(key, value)
    click.echo(f"Set '{key}'.")


@cli.command("get")
@click.argument("key")
@click.option("--vault", "vault_path", default=str(DEFAULT_VAULT), show_default=True, type=click.Path(path_type=Path))
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def get_cmd(key: str, vault_path: Path, password: str) -> None:
    """Get the value of KEY from the vault."""
    try:
        vault = get_vault(vault_path, password)
    except VaultNotFoundError:
        click.echo("Vault not found.", err=True)
        raise SystemExit(1)
    value = vault.get(key)
    if value is None:
        click.echo(f"Key '{key}' not found.", err=True)
        raise SystemExit(1)
    click.echo(value)


@cli.command("delete")
@click.argument("key")
@click.option("--vault", "vault_path", default=str(DEFAULT_VAULT), show_default=True, type=click.Path(path_type=Path))
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def delete_cmd(key: str, vault_path: Path, password: str) -> None:
    """Delete KEY from the vault."""
    try:
        vault = get_vault(vault_path, password)
    except VaultNotFoundError:
        click.echo("Vault not found.", err=True)
        raise SystemExit(1)
    deleted = vault.delete(key)
    if deleted:
        click.echo(f"Deleted '{key}'.")
    else:
        click.echo(f"Key '{key}' not found.", err=True)
        raise SystemExit(1)


@cli.command("list")
@click.option("--vault", "vault_path", default=str(DEFAULT_VAULT), show_default=True, type=click.Path(path_type=Path))
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def list_cmd(vault_path: Path, password: str) -> None:
    """List all keys stored in the vault."""
    try:
        vault = get_vault(vault_path, password)
    except VaultNotFoundError:
        click.echo("Vault not found.", err=True)
        raise SystemExit(1)
    keys = vault.keys()
    if not keys:
        click.echo("Vault is empty.")
    else:
        for key in sorted(keys):
            click.echo(key)
