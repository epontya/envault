"""CLI commands for vault locking."""

from __future__ import annotations

from pathlib import Path

import click

from envault.lock import lock_vault, unlock_vault, is_locked, lock_info, LockError


@click.group("lock")
def lock_group() -> None:
    """Lock and unlock the vault to prevent accidental writes."""


@lock_group.command("on")
@click.option("--vault", "vault_path", required=True, type=click.Path(), help="Path to vault file.")
@click.option("--reason", default="manual", show_default=True, help="Reason for locking.")
def lock_on(vault_path: str, reason: str) -> None:
    """Lock the vault."""
    path = Path(vault_path)
    if not path.exists():
        click.echo(f"Error: vault file '{vault_path}' not found.", err=True)
        raise SystemExit(1)
    if is_locked(path):
        click.echo("Vault is already locked.")
        return
    record = lock_vault(path, reason=reason)
    import time
    ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(record["locked_at"]))
    click.echo(f"Vault locked at {ts} (reason: {reason}).")


@lock_group.command("off")
@click.option("--vault", "vault_path", required=True, type=click.Path(), help="Path to vault file.")
def lock_off(vault_path: str) -> None:
    """Unlock the vault."""
    path = Path(vault_path)
    removed = unlock_vault(path)
    if removed:
        click.echo("Vault unlocked.")
    else:
        click.echo("Vault was not locked.")


@lock_group.command("status")
@click.option("--vault", "vault_path", required=True, type=click.Path(), help="Path to vault file.")
def lock_status(vault_path: str) -> None:
    """Show lock status of the vault."""
    path = Path(vault_path)
    try:
        info = lock_info(path)
    except LockError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    if info is None:
        click.echo("Status: unlocked")
    else:
        import time
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(info.get("locked_at", 0)))
        click.echo(f"Status: locked")
        click.echo(f"  Since : {ts}")
        click.echo(f"  Reason: {info.get('reason', 'unknown')}")
