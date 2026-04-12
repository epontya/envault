"""CLI commands for managing key namespaces."""

from __future__ import annotations

from pathlib import Path

import click

from envault.namespace import NamespaceError, NamespaceStore


def _ns(vault_file: str) -> NamespaceStore:
    store_path = Path(vault_file).with_suffix(".namespaces.json")
    return NamespaceStore(store_path)


@click.group("namespace")
def namespace_group() -> None:
    """Manage key namespaces."""


@namespace_group.command("assign")
@click.argument("key")
@click.argument("namespace")
@click.option("--vault", default="vault.db", show_default=True, help="Vault file path.")
def namespace_assign(key: str, namespace: str, vault: str) -> None:
    """Assign KEY to NAMESPACE."""
    try:
        _ns(vault).assign(key, namespace)
        click.echo(f"Assigned '{key}' to namespace '{namespace}'.")
    except NamespaceError as exc:
        raise click.ClickException(str(exc)) from exc


@namespace_group.command("get")
@click.argument("key")
@click.option("--vault", default="vault.db", show_default=True)
def namespace_get(key: str, vault: str) -> None:
    """Print the namespace for KEY."""
    ns = _ns(vault).get_namespace(key)
    if ns is None:
        raise click.ClickException(f"Key '{key}' has no namespace assignment.")
    click.echo(ns)


@namespace_group.command("list")
@click.argument("namespace")
@click.option("--vault", default="vault.db", show_default=True)
def namespace_list(namespace: str, vault: str) -> None:
    """List all keys in NAMESPACE."""
    keys = _ns(vault).keys_in(namespace)
    if not keys:
        click.echo(f"No keys in namespace '{namespace}'.")
        return
    for key in keys:
        click.echo(key)


@namespace_group.command("namespaces")
@click.option("--vault", default="vault.db", show_default=True)
def namespace_namespaces(vault: str) -> None:
    """List all known namespaces."""
    namespaces = _ns(vault).list_namespaces()
    if not namespaces:
        click.echo("No namespaces defined.")
        return
    for ns in namespaces:
        click.echo(ns)


@namespace_group.command("unassign")
@click.argument("key")
@click.option("--vault", default="vault.db", show_default=True)
def namespace_unassign(key: str, vault: str) -> None:
    """Remove namespace assignment for KEY."""
    removed = _ns(vault).unassign(key)
    if removed:
        click.echo(f"Unassigned '{key}' from its namespace.")
    else:
        raise click.ClickException(f"Key '{key}' has no namespace assignment.")


@namespace_group.command("rename")
@click.argument("old")
@click.argument("new")
@click.option("--vault", default="vault.db", show_default=True)
def namespace_rename(old: str, new: str, vault: str) -> None:
    """Rename namespace OLD to NEW."""
    try:
        count = _ns(vault).rename(old, new)
        click.echo(f"Renamed namespace '{old}' -> '{new}' ({count} key(s) updated).")
    except NamespaceError as exc:
        raise click.ClickException(str(exc)) from exc
