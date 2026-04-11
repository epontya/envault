"""CLI commands for vault snapshots."""

from __future__ import annotations

import click
from pathlib import Path

from envault.cli import get_vault
from envault.snapshot import (
    SnapshotError,
    save_snapshot,
    restore_snapshot,
    list_snapshots,
    delete_snapshot,
)

_DEFAULT_SNAP_DIR = Path.home() / ".envault" / "snapshots"


@click.group("snapshot")
def snapshot_group() -> None:
    """Manage vault snapshots."""


@snapshot_group.command("save")
@click.argument("name")
@click.option("--vault-file", default="vault.db", show_default=True)
@click.option("--snap-dir", default=str(_DEFAULT_SNAP_DIR), show_default=True)
@click.password_option("--password", envvar="ENVAULT_PASSWORD", prompt="Vault password")
def snapshot_save(name: str, vault_file: str, snap_dir: str, password: str) -> None:
    """Save a snapshot of the current vault state."""
    vault = get_vault(vault_file, password)
    try:
        payload = save_snapshot(vault, name, Path(snap_dir), password)
        count = len(payload["entries"])
        click.echo(f"Snapshot '{name}' saved ({count} key(s)).")
    except SnapshotError as exc:
        raise click.ClickException(str(exc)) from exc


@snapshot_group.command("restore")
@click.argument("name")
@click.option("--vault-file", default="vault.db", show_default=True)
@click.option("--snap-dir", default=str(_DEFAULT_SNAP_DIR), show_default=True)
@click.option("--no-overwrite", is_flag=True, default=False)
@click.password_option("--password", envvar="ENVAULT_PASSWORD", prompt="Vault password")
def snapshot_restore(
    name: str, vault_file: str, snap_dir: str, no_overwrite: bool, password: str
) -> None:
    """Restore vault entries from a snapshot."""
    vault = get_vault(vault_file, password)
    try:
        count = restore_snapshot(
            vault, name, Path(snap_dir), password, overwrite=not no_overwrite
        )
        click.echo(f"Restored {count} key(s) from snapshot '{name}'.")
    except SnapshotError as exc:
        raise click.ClickException(str(exc)) from exc


@snapshot_group.command("list")
@click.option("--snap-dir", default=str(_DEFAULT_SNAP_DIR), show_default=True)
def snapshot_list(snap_dir: str) -> None:
    """List available snapshots."""
    names = list_snapshots(Path(snap_dir))
    if not names:
        click.echo("No snapshots found.")
    else:
        for name in names:
            click.echo(name)


@snapshot_group.command("delete")
@click.argument("name")
@click.option("--snap-dir", default=str(_DEFAULT_SNAP_DIR), show_default=True)
def snapshot_delete(name: str, snap_dir: str) -> None:
    """Delete a snapshot by name."""
    if delete_snapshot(name, Path(snap_dir)):
        click.echo(f"Snapshot '{name}' deleted.")
    else:
        raise click.ClickException(f"Snapshot '{name}' not found.")
