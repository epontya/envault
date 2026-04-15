"""CLI commands for managing vault key watches."""

from __future__ import annotations

from pathlib import Path

import click

from envault.cli import get_vault
from envault.watch import WatchError, add_watch, check_watches, list_watches, remove_watch


@click.group("watch")
def watch_group() -> None:
    """Watch vault keys for changes."""


@watch_group.command("add")
@click.argument("vault_file")
@click.argument("key")
@click.argument("label")
@click.option("--password", prompt=True, hide_input=True)
def watch_add(vault_file: str, key: str, label: str, password: str) -> None:
    """Add a watch on KEY with notification LABEL."""
    vault = get_vault(vault_file, password)
    current = vault.get(key)
    try:
        entry = add_watch(Path(vault_file), key, label, current)
        click.echo(f"Watching '{entry.key}' with label '{entry.callback_label}'.")
    except WatchError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@watch_group.command("remove")
@click.argument("vault_file")
@click.argument("key")
def watch_remove(vault_file: str, key: str) -> None:
    """Remove the watch on KEY."""
    removed = remove_watch(Path(vault_file), key)
    if removed:
        click.echo(f"Watch on '{key}' removed.")
    else:
        click.echo(f"No watch found for '{key}'.", err=True)
        raise SystemExit(1)


@watch_group.command("list")
@click.argument("vault_file")
def watch_list(vault_file: str) -> None:
    """List all active watches for a vault."""
    entries = list_watches(Path(vault_file))
    if not entries:
        click.echo("No active watches.")
        return
    for e in entries:
        click.echo(f"{e.key}  label={e.callback_label}  last_value={e.last_value!r}  since={e.created_at}")


@watch_group.command("check")
@click.argument("vault_file")
@click.option("--password", prompt=True, hide_input=True)
def watch_check(vault_file: str, password: str) -> None:
    """Check all watched keys for changes since last check."""
    vault = get_vault(vault_file, password)
    watches = list_watches(Path(vault_file))
    current = {e.key: vault.get(e.key) for e in watches}
    changed = check_watches(Path(vault_file), current)
    if not changed:
        click.echo("No changes detected.")
    else:
        for e in changed:
            click.echo(f"CHANGED  {e.key}  label={e.callback_label}  new_value={e.last_value!r}")
