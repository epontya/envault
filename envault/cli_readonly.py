"""CLI commands for read-only key protection."""
from __future__ import annotations

import click

from envault.env_readonly import (
    ReadOnlyError,
    protect,
    unprotect,
    is_protected,
    list_protected,
)


@click.group("readonly", help="Protect vault keys from modification.")
def readonly_group() -> None:
    pass


@readonly_group.command("protect")
@click.argument("vault_path")
@click.argument("key")
def readonly_protect(vault_path: str, key: str) -> None:
    """Mark KEY as read-only in VAULT_PATH."""
    try:
        keys = protect(vault_path, key)
        click.echo(f"Protected '{key}'. Total protected keys: {len(keys)}.")
    except ReadOnlyError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@readonly_group.command("unprotect")
@click.argument("vault_path")
@click.argument("key")
def readonly_unprotect(vault_path: str, key: str) -> None:
    """Remove read-only protection from KEY in VAULT_PATH."""
    removed = unprotect(vault_path, key)
    if removed:
        click.echo(f"Protection removed from '{key}'.")
    else:
        click.echo(f"Key '{key}' was not protected.", err=True)
        raise SystemExit(1)


@readonly_group.command("check")
@click.argument("vault_path")
@click.argument("key")
def readonly_check(vault_path: str, key: str) -> None:
    """Check whether KEY is read-only in VAULT_PATH."""
    if is_protected(vault_path, key):
        click.echo(f"'{key}' is protected (read-only).")
    else:
        click.echo(f"'{key}' is writable.")


@readonly_group.command("list")
@click.argument("vault_path")
def readonly_list(vault_path: str) -> None:
    """List all read-only keys in VAULT_PATH."""
    keys = list_protected(vault_path)
    if not keys:
        click.echo("No keys are currently protected.")
    else:
        for k in keys:
            click.echo(k)
