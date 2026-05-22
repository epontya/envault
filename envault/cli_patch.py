"""CLI commands for patching vault entries."""
from __future__ import annotations

import json
import sys

import click

from envault.cli import get_vault
from envault.env_patch import PatchError, apply_patch


@click.group("patch")
def patch_group() -> None:
    """Patch (partial-update) vault entries."""


@patch_group.command("apply")
@click.argument("vault_file", type=click.Path())
@click.option("--password", "-p", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.option(
    "--set", "sets",
    multiple=True,
    metavar="KEY=VALUE",
    help="Set KEY to VALUE (may be repeated).",
)
@click.option(
    "--remove", "removes",
    multiple=True,
    metavar="KEY",
    help="Remove KEY from vault (may be repeated).",
)
@click.option("--no-add", is_flag=True, default=False, help="Skip keys not already in vault.")
@click.option("--keep-nulls", is_flag=True, default=False, help="Do not remove keys set to null.")
def patch_apply(
    vault_file: str,
    password: str,
    sets: tuple,
    removes: tuple,
    no_add: bool,
    keep_nulls: bool,
) -> None:
    """Apply a partial update to a vault."""
    patch: dict = {}

    for item in sets:
        if "=" not in item:
            click.echo(f"Error: --set value must be KEY=VALUE, got {item!r}", err=True)
            sys.exit(1)
        k, v = item.split("=", 1)
        patch[k] = v

    for key in removes:
        patch[key] = None

    if not patch:
        click.echo("Nothing to patch.", err=True)
        sys.exit(1)

    try:
        vault = get_vault(vault_file, password)
        summary = apply_patch(vault, patch, add_new=not no_add, remove_nulls=not keep_nulls)
    except PatchError as exc:
        click.echo(f"Patch error: {exc}", err=True)
        sys.exit(1)

    added = summary["added"]
    updated = summary["updated"]
    removed = summary["removed"]

    if added:
        click.echo(f"Added   : {', '.join(added)}")
    if updated:
        click.echo(f"Updated : {', '.join(updated)}")
    if removed:
        click.echo(f"Removed : {', '.join(removed)}")
    if not (added or updated or removed):
        click.echo("No changes applied.")
