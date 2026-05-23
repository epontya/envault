"""Integration helpers: guard vault set/delete against read-only keys."""
from __future__ import annotations

import click

from envault.cli import get_vault
from envault.env_readonly import ReadOnlyError, assert_writable


@click.group("ro-ops", help="Vault operations that respect read-only protection.")
def ro_ops_group() -> None:
    pass


@ro_ops_group.command("set")
@click.argument("vault_path")
@click.argument("key")
@click.argument("value")
@click.password_option("--password", prompt="Vault password")
def ro_set(vault_path: str, key: str, value: str, password: str) -> None:
    """Set KEY=VALUE, respecting read-only protection."""
    try:
        assert_writable(vault_path, key)
    except ReadOnlyError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    vault = get_vault(vault_path, password)
    vault.set(key, value)
    click.echo(f"Set '{key}'.")


@ro_ops_group.command("delete")
@click.argument("vault_path")
@click.argument("key")
@click.password_option("--password", prompt="Vault password")
def ro_delete(vault_path: str, key: str, password: str) -> None:
    """Delete KEY, respecting read-only protection."""
    try:
        assert_writable(vault_path, key)
    except ReadOnlyError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    vault = get_vault(vault_path, password)
    deleted = vault.delete(key)
    if deleted:
        click.echo(f"Deleted '{key}'.")
    else:
        click.echo(f"Key '{key}' not found.", err=True)
        raise SystemExit(1)
