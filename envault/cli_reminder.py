"""CLI commands for managing key reminders."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import click

from envault.cli import get_vault
from envault.reminder import (
    ReminderError,
    due_reminders,
    get_reminder,
    list_reminders,
    remove_reminder,
    set_reminder,
)


@click.group("reminder")
def reminder_group() -> None:
    """Manage key rotation / review reminders."""


@reminder_group.command("set")
@click.argument("key")
@click.argument("remind_at")  # ISO-8601, e.g. 2025-12-01T09:00:00+00:00
@click.option("--note", default="", help="Optional note attached to the reminder.")
@click.option("--vault", "vault_path", default=".envault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def reminder_set(key: str, remind_at: str, note: str, vault_path: str, password: str) -> None:
    """Set a reminder for KEY at REMIND_AT (ISO-8601 datetime)."""
    vault = get_vault(Path(vault_path), password)
    if vault.get(key) is None:
        raise click.ClickException(f"Key '{key}' not found in vault.")
    try:
        dt = datetime.fromisoformat(remind_at)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
    except ValueError:
        raise click.ClickException(f"Invalid datetime format: {remind_at}")
    try:
        entry = set_reminder(Path(vault_path), key, dt, note=note)
    except ReminderError as exc:
        raise click.ClickException(str(exc))
    click.echo(f"Reminder set for '{key}' at {entry['remind_at']}.")


@reminder_group.command("remove")
@click.argument("key")
@click.option("--vault", "vault_path", default=".envault", show_default=True)
def reminder_remove(key: str, vault_path: str) -> None:
    """Remove the reminder for KEY."""
    removed = remove_reminder(Path(vault_path), key)
    if removed:
        click.echo(f"Reminder for '{key}' removed.")
    else:
        raise click.ClickException(f"No reminder found for '{key}'.")


@reminder_group.command("list")
@click.option("--vault", "vault_path", default=".envault", show_default=True)
@click.option("--due", is_flag=True, help="Show only reminders that are currently due.")
def reminder_list(vault_path: str, due: bool) -> None:
    """List all reminders (or only due ones with --due)."""
    vp = Path(vault_path)
    entries = due_reminders(vp) if due else list_reminders(vp)
    if not entries:
        click.echo("No reminders found.")
        return
    for e in entries:
        note_part = f" — {e['note']}" if e["note"] else ""
        click.echo(f"{e['key']:30s}  {e['remind_at']}{note_part}")
