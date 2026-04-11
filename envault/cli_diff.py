"""CLI commands for diffing vault snapshots."""
from __future__ import annotations

import click

from envault.cli import get_vault
from envault.diff import diff_snapshot_vs_vault, diff_two_snapshots, DiffError


@click.group("diff")
def diff_group() -> None:
    """Compare vault snapshots or snapshot vs live vault."""


@diff_group.command("snapshot")
@click.argument("snapshot_name")
@click.option("--vault-file", default="vault.db", show_default=True, help="Path to vault file.")
@click.option("--snap-dir", default=None, help="Directory where snapshots are stored.")
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False)
def diff_snapshot(
    snapshot_name: str,
    vault_file: str,
    snap_dir: str | None,
    password: str,
) -> None:
    """Show diff between SNAPSHOT_NAME and the current live vault."""
    vault = get_vault(vault_file, password)
    try:
        result = diff_snapshot_vs_vault(vault, password, snapshot_name, snap_dir=snap_dir)
    except (DiffError, Exception) as exc:
        raise click.ClickException(str(exc)) from exc

    if result.has_changes:
        click.echo(f"Changes between snapshot '{snapshot_name}' and live vault:")
        click.echo(result.summary())
    else:
        click.echo(f"No changes between snapshot '{snapshot_name}' and live vault.")


@diff_group.command("snapshots")
@click.argument("snap_a")
@click.argument("snap_b")
@click.option("--vault-file", default="vault.db", show_default=True, help="Path to vault file.")
@click.option("--snap-dir", default=None, help="Directory where snapshots are stored.")
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False)
def diff_snapshots(
    snap_a: str,
    snap_b: str,
    vault_file: str,
    snap_dir: str | None,
    password: str,
) -> None:
    """Show diff between SNAP_A (old) and SNAP_B (new)."""
    vault = get_vault(vault_file, password)
    try:
        result = diff_two_snapshots(vault, password, snap_a, snap_b, snap_dir=snap_dir)
    except (DiffError, Exception) as exc:
        raise click.ClickException(str(exc)) from exc

    if result.has_changes:
        click.echo(f"Changes from '{snap_a}' to '{snap_b}':")
        click.echo(result.summary())
    else:
        click.echo(f"No changes between '{snap_a}' and '{snap_b}'.")
