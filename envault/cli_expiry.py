"""CLI commands for managing key expiry dates."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import click

from envault.expiry import ExpiryError, ExpiryStore
from envault.cli import get_vault


def _es(vault_file: str) -> ExpiryStore:
    vf = Path(vault_file)
    return ExpiryStore(vf.parent / (vf.stem + ".expiry.json"))


@click.group("expiry")
def expiry_group() -> None:
    """Manage key expiration dates."""


@expiry_group.command("set")
@click.argument("key")
@click.argument("expires_at")  # ISO-8601 string, e.g. 2025-12-31T23:59:59+00:00
@click.option("--vault", "vault_file", required=True, help="Path to vault file.")
def expiry_set(key: str, expires_at: str, vault_file: str) -> None:
    """Set an expiration date for KEY."""
    vault = get_vault(vault_file)
    if vault.get(key) is None:
        raise click.ClickException(f"Key '{key}' not found in vault.")
    try:
        dt = datetime.fromisoformat(expires_at)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        _es(vault_file).set_expiry(key, dt)
        click.echo(f"Expiry for '{key}' set to {dt.isoformat()}.")
    except (ValueError, ExpiryError) as exc:
        raise click.ClickException(str(exc)) from exc


@expiry_group.command("get")
@click.argument("key")
@click.option("--vault", "vault_file", required=True, help="Path to vault file.")
def expiry_get(key: str, vault_file: str) -> None:
    """Show the expiration date for KEY."""
    es = _es(vault_file)
    exp = es.get_expiry(key)
    if exp is None:
        click.echo(f"No expiry set for '{key}'.")
    else:
        status = "EXPIRED" if es.is_expired(key) else "active"
        click.echo(f"{key}: {exp.isoformat()} [{status}]")


@expiry_group.command("remove")
@click.argument("key")
@click.option("--vault", "vault_file", required=True, help="Path to vault file.")
def expiry_remove(key: str, vault_file: str) -> None:
    """Remove the expiration date for KEY."""
    removed = _es(vault_file).remove(key)
    if removed:
        click.echo(f"Expiry removed for '{key}'.")
    else:
        click.echo(f"No expiry was set for '{key}'.")


@expiry_group.command("list")
@click.option("--vault", "vault_file", required=True, help="Path to vault file.")
@click.option("--expired-only", is_flag=True, help="Show only expired keys.")
def expiry_list(vault_file: str, expired_only: bool) -> None:
    """List keys with expiration dates."""
    es = _es(vault_file)
    entries = es.list_all()
    if not entries:
        click.echo("No expiry dates set.")
        return
    for key, exp in sorted(entries.items()):
        is_exp = es.is_expired(key)
        if expired_only and not is_exp:
            continue
        status = "EXPIRED" if is_exp else "active"
        click.echo(f"{key}: {exp.isoformat()} [{status}]")
