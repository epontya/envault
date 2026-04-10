"""CLI commands for profile management, registered on the main cli group."""

from __future__ import annotations

from pathlib import Path

import click

from envault.profiles import ProfileManager, ProfileNotFoundError


def _pm() -> ProfileManager:
    return ProfileManager()


@click.group("profile")
def profile_group() -> None:
    """Manage named vault profiles."""


@profile_group.command("add")
@click.argument("name")
@click.argument("vault_path", type=click.Path(dir_okay=False, path_type=Path))
def profile_add(name: str, vault_path: Path) -> None:
    """Register NAME as a profile pointing to VAULT_PATH."""
    pm = _pm()
    pm.add(name, vault_path)
    click.echo(f"Profile '{name}' -> {vault_path}")


@profile_group.command("remove")
@click.argument("name")
def profile_remove(name: str) -> None:
    """Remove a profile by NAME."""
    pm = _pm()
    if pm.remove(name):
        click.echo(f"Profile '{name}' removed.")
    else:
        click.echo(f"Profile '{name}' not found.", err=True)
        raise SystemExit(1)


@profile_group.command("list")
def profile_list() -> None:
    """List all registered profiles."""
    pm = _pm()
    names = pm.list_profiles()
    if not names:
        click.echo("No profiles registered.")
        return
    for name in names:
        path = pm.get_path(name)
        click.echo(f"{name}\t{path}")


@profile_group.command("rename")
@click.argument("old_name")
@click.argument("new_name")
def profile_rename(old_name: str, new_name: str) -> None:
    """Rename a profile from OLD_NAME to NEW_NAME."""
    pm = _pm()
    try:
        pm.rename(old_name, new_name)
        click.echo(f"Profile '{old_name}' renamed to '{new_name}'.")
    except ProfileNotFoundError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1) from exc


@profile_group.command("show")
@click.argument("name")
def profile_show(name: str) -> None:
    """Show the vault path for a profile."""
    pm = _pm()
    try:
        path = pm.get_path(name)
        click.echo(str(path))
    except ProfileNotFoundError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1) from exc
