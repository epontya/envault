"""CLI commands for session (password cache) management."""

from __future__ import annotations

from pathlib import Path

import click

from envault.session import SessionError, get_store

_DEFAULT_TTL = 900


@click.group("session")
def session_group() -> None:
    """Manage the in-memory password session cache."""


@session_group.command("unlock")
@click.argument("vault_file", type=click.Path(exists=True, dir_okay=False))
@click.option("--ttl", default=_DEFAULT_TTL, show_default=True, help="Cache lifetime in seconds.")
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False)
def session_unlock(vault_file: str, ttl: int, password: str) -> None:
    """Cache the vault password for VAULT_FILE so subsequent commands skip the prompt."""
    store = get_store()
    try:
        entry = store.set(Path(vault_file), password, ttl=ttl)
    except SessionError as exc:
        raise click.ClickException(str(exc)) from exc
    mins = entry.seconds_remaining() / 60
    click.echo(f"Session active for {mins:.1f} minute(s).")


@session_group.command("lock")
@click.argument("vault_file", type=click.Path(dir_okay=False))
def session_lock(vault_file: str) -> None:
    """Immediately clear the cached password for VAULT_FILE."""
    store = get_store()
    removed = store.clear(Path(vault_file))
    if removed:
        click.echo("Session cleared.")
    else:
        click.echo("No active session found.")


@session_group.command("lock-all")
def session_lock_all() -> None:
    """Clear all cached passwords."""
    count = get_store().clear_all()
    click.echo(f"Cleared {count} session(s).")


@session_group.command("status")
@click.argument("vault_file", type=click.Path(dir_okay=False))
def session_status(vault_file: str) -> None:
    """Show whether a session is active for VAULT_FILE."""
    entry = get_store().status(Path(vault_file))
    if entry is None:
        click.echo("No active session.")
    else:
        secs = entry.seconds_remaining()
        click.echo(f"Session active — {secs:.0f}s remaining (expires {entry.expires_at:.0f}).")
