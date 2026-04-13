"""CLI commands for vault backup and restore."""

from __future__ import annotations

from pathlib import Path

import click

from envault.backup import BackupError, create_backup, delete_backup, list_backups, restore_backup


@click.group("backup")
def backup_group() -> None:
    """Backup and restore vault files."""


@backup_group.command("create")
@click.argument("vault_file", type=click.Path(exists=True))
@click.option("--label", default="", help="Optional human-readable label for this backup.")
def backup_create(vault_file: str, label: str) -> None:
    """Create a backup of VAULT_FILE."""
    try:
        entry = create_backup(Path(vault_file), label or None)
        click.echo(f"Backup created: {entry['filename']}")
        if entry["label"]:
            click.echo(f"Label: {entry['label']}")
    except BackupError as exc:
        raise click.ClickException(str(exc)) from exc


@backup_group.command("list")
@click.argument("vault_file", type=click.Path())
def backup_list(vault_file: str) -> None:
    """List all backups for VAULT_FILE."""
    backups = list_backups(Path(vault_file))
    if not backups:
        click.echo("No backups found.")
        return
    for entry in backups:
        label_part = f"  [{entry['label']}]" if entry["label"] else ""
        click.echo(f"{entry['filename']}  {entry['created_at']}{label_part}")


@backup_group.command("restore")
@click.argument("vault_file", type=click.Path())
@click.argument("filename")
def backup_restore(vault_file: str, filename: str) -> None:
    """Restore FILENAME backup into VAULT_FILE."""
    try:
        restore_backup(Path(vault_file), filename)
        click.echo(f"Vault restored from {filename}.")
    except BackupError as exc:
        raise click.ClickException(str(exc)) from exc


@backup_group.command("delete")
@click.argument("vault_file", type=click.Path())
@click.argument("filename")
def backup_delete(vault_file: str, filename: str) -> None:
    """Delete a specific backup FILENAME for VAULT_FILE."""
    try:
        delete_backup(Path(vault_file), filename)
        click.echo(f"Backup {filename} deleted.")
    except BackupError as exc:
        raise click.ClickException(str(exc)) from exc
