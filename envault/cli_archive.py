"""CLI commands for archiving and restoring vault entries."""
from __future__ import annotations

import click

from envault.cli import get_vault
from envault.env_archive import (
    ArchiveError,
    archive_key,
    list_archived,
    purge_all,
    purge_key,
    restore_key,
)


@click.group("archive")
def archive_group() -> None:
    """Soft-delete and recover vault entries."""


@archive_group.command("move")
@click.argument("key")
@click.option("--vault", "vault_path", required=True, help="Path to vault file.")
@click.option("--password", prompt=True, hide_input=True)
def archive_move(key: str, vault_path: str, password: str) -> None:
    """Archive (soft-delete) a key from the vault."""
    v = get_vault(vault_path, password)
    value = v.get(key)
    if value is None:
        click.echo(f"Key '{key}' not found in vault.", err=True)
        raise SystemExit(1)
    v.delete(key)
    entry = archive_key(vault_path, key, value)
    click.echo(f"Archived '{key}' at {entry['archived_at']}.")


@archive_group.command("restore")
@click.argument("key")
@click.option("--vault", "vault_path", required=True, help="Path to vault file.")
@click.option("--password", prompt=True, hide_input=True)
def archive_restore(key: str, vault_path: str, password: str) -> None:
    """Restore an archived key back into the vault."""
    value = restore_key(vault_path, key)
    if value is None:
        click.echo(f"Key '{key}' not found in archive.", err=True)
        raise SystemExit(1)
    v = get_vault(vault_path, password)
    v.set(key, value)
    click.echo(f"Restored '{key}' to vault.")


@archive_group.command("list")
@click.option("--vault", "vault_path", required=True, help="Path to vault file.")
def archive_list(vault_path: str) -> None:
    """List all archived entries."""
    entries = list_archived(vault_path)
    if not entries:
        click.echo("No archived entries.")
        return
    for e in entries:
        click.echo(f"{e['key']}  (archived {e['archived_at']})")


@archive_group.command("purge")
@click.argument("key")
@click.option("--vault", "vault_path", required=True, help="Path to vault file.")
def archive_purge(key: str, vault_path: str) -> None:
    """Permanently delete a single archived entry."""
    removed = purge_key(vault_path, key)
    if not removed:
        click.echo(f"Key '{key}' not found in archive.", err=True)
        raise SystemExit(1)
    click.echo(f"Purged '{key}' from archive.")


@archive_group.command("purge-all")
@click.option("--vault", "vault_path", required=True, help="Path to vault file.")
@click.confirmation_option(prompt="Permanently delete ALL archived entries?")
def archive_purge_all(vault_path: str) -> None:
    """Permanently delete every archived entry."""
    count = purge_all(vault_path)
    click.echo(f"Purged {count} archived entry/entries.")
