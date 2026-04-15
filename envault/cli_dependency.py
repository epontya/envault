"""CLI commands for managing key dependencies."""
from __future__ import annotations

from pathlib import Path

import click

from envault.dependency import DependencyError, DependencyStore


def _ds(vault_path: str) -> DependencyStore:
    return DependencyStore(Path(vault_path))


@click.group("dep")
def dep_group() -> None:
    """Manage dependencies between vault keys."""


@dep_group.command("add")
@click.option("--vault", required=True, help="Path to the vault file.")
@click.argument("key")
@click.argument("depends_on")
def dep_add(vault: str, key: str, depends_on: str) -> None:
    """Record that KEY depends on DEPENDS_ON."""
    try:
        _ds(vault).add(key, depends_on)
        click.echo(f"Added dependency: {key} -> {depends_on}")
    except DependencyError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@dep_group.command("remove")
@click.option("--vault", required=True, help="Path to the vault file.")
@click.argument("key")
@click.argument("depends_on")
def dep_remove(vault: str, key: str, depends_on: str) -> None:
    """Remove a dependency edge from KEY -> DEPENDS_ON."""
    removed = _ds(vault).remove(key, depends_on)
    if removed:
        click.echo(f"Removed dependency: {key} -> {depends_on}")
    else:
        click.echo(f"Dependency not found: {key} -> {depends_on}", err=True)
        raise SystemExit(1)


@dep_group.command("list")
@click.option("--vault", required=True, help="Path to the vault file.")
@click.argument("key")
@click.option("--transitive", is_flag=True, help="Show all transitive dependencies.")
def dep_list(vault: str, key: str, transitive: bool) -> None:
    """List dependencies of KEY."""
    ds = _ds(vault)
    if transitive:
        deps = sorted(ds.all_dependencies(key))
        label = "transitive dependencies"
    else:
        deps = ds.get(key)
        label = "direct dependencies"
    if deps:
        click.echo(f"{key} {label}: {', '.join(deps)}")
    else:
        click.echo(f"{key} has no {label}.")


@dep_group.command("dependents")
@click.option("--vault", required=True, help="Path to the vault file.")
@click.argument("key")
def dep_dependents(vault: str, key: str) -> None:
    """List all keys that directly depend on KEY."""
    result = _ds(vault).dependents(key)
    if result:
        click.echo(f"Keys depending on {key}: {', '.join(sorted(result))}")
    else:
        click.echo(f"No keys depend on {key}.")
