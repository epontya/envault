"""CLI commands for viewing vault entry history."""

from __future__ import annotations

import datetime
from pathlib import Path

import click

from envault.cli import get_vault
from envault.history import HistoryStore


def _hs(vault_file: str) -> HistoryStore:
    p = Path(vault_file)
    return HistoryStore(p.parent / (p.stem + ".history.json"))


@click.group("history")
def history_group():
    """View and manage entry change history."""


@history_group.command("log")
@click.argument("key")
@click.option("--vault", default="vault.db", show_default=True, help="Vault file path.")
def history_log(key: str, vault: str):
    """Show change history for KEY."""
    hs = _hs(vault)
    entries = hs.get(key)
    if not entries:
        click.echo(f"No history found for '{key}'.")
        return
    for e in entries:
        ts = datetime.datetime.fromtimestamp(e.timestamp).strftime("%Y-%m-%d %H:%M:%S")
        val = e.value if e.value is not None else "<deleted>"
        click.echo(f"[{ts}] {e.action.upper():6s}  {key}={val}")


@history_group.command("clear")
@click.argument("key", required=False, default=None)
@click.option("--vault", default="vault.db", show_default=True, help="Vault file path.")
@click.option("--yes", is_flag=True, help="Skip confirmation prompt.")
def history_clear(key: str | None, vault: str, yes: bool):
    """Clear history for KEY (or all history if KEY is omitted)."""
    hs = _hs(vault)
    target = f"key '{key}'" if key else "ALL entries"
    if not yes:
        click.confirm(f"Clear history for {target}?", abort=True)
    removed = hs.clear(key)
    click.echo(f"Removed {removed} history record(s).")


@history_group.command("all")
@click.option("--vault", default="vault.db", show_default=True, help="Vault file path.")
@click.option("--limit", default=20, show_default=True, help="Max entries to show.")
def history_all(vault: str, limit: int):
    """Show recent history across all keys."""
    hs = _hs(vault)
    entries = hs.all()[-limit:]
    if not entries:
        click.echo("No history recorded yet.")
        return
    for e in entries:
        ts = datetime.datetime.fromtimestamp(e.timestamp).strftime("%Y-%m-%d %H:%M:%S")
        val = e.value if e.value is not None else "<deleted>"
        click.echo(f"[{ts}] {e.action.upper():6s}  {e.key}={val}")
