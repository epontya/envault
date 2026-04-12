"""CLI commands for PIN quick-unlock management."""

from __future__ import annotations

from pathlib import Path

import click

from envault.pin import PINError, PINStore

DEFAULT_PIN_FILE = Path.home() / ".envault" / "pin_session.json"


def _ps(pin_file: Path | None = None) -> PINStore:
    return PINStore(pin_file or DEFAULT_PIN_FILE)


@click.group("pin")
def pin_group() -> None:
    """Manage PIN quick-unlock sessions."""


@pin_group.command("set")
@click.option("--pin-file", type=click.Path(), default=None, hidden=True)
@click.argument("pin")
@click.password_option("--password", prompt="Master password", help="Vault master password.")
def pin_set(pin: str, password: str, pin_file: str | None) -> None:
    """Set a PIN to quickly unlock the vault for this session."""
    store = _ps(Path(pin_file) if pin_file else None)
    try:
        store.set_pin(pin, password)
        click.echo("PIN set. Session valid for 1 hour.")
    except PINError as exc:
        raise click.ClickException(str(exc)) from exc


@pin_group.command("unlock")
@click.option("--pin-file", type=click.Path(), default=None, hidden=True)
@click.argument("pin")
def pin_unlock(pin: str, pin_file: str | None) -> None:
    """Unlock the session using a PIN and print the stored password."""
    store = _ps(Path(pin_file) if pin_file else None)
    try:
        password = store.unlock(pin)
        click.echo(password)
    except PINError as exc:
        raise click.ClickException(str(exc)) from exc


@pin_group.command("clear")
@click.option("--pin-file", type=click.Path(), default=None, hidden=True)
def pin_clear(pin_file: str | None) -> None:
    """Clear the current PIN session."""
    store = _ps(Path(pin_file) if pin_file else None)
    store.clear()
    click.echo("PIN session cleared.")


@pin_group.command("status")
@click.option("--pin-file", type=click.Path(), default=None, hidden=True)
def pin_status(pin_file: str | None) -> None:
    """Show whether a PIN session is currently active."""
    store = _ps(Path(pin_file) if pin_file else None)
    if store.is_set():
        click.echo("PIN session is active.")
    else:
        click.echo("No active PIN session.")
