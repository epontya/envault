"""CLI commands for vault sync operations."""

from __future__ import annotations

from pathlib import Path

import click

from envault.cli import get_vault
from envault.sync import SyncError, pull_from_file, push_to_file


@click.group("sync")
def sync_group() -> None:
    """Push or pull vault contents to/from an encrypted sync file."""


@sync_group.command("push")
@click.argument("dest", type=click.Path(dir_okay=False, writable=True))
@click.option(
    "--vault-file",
    default=".envault",
    show_default=True,
    help="Path to the local vault file.",
)
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False)
def sync_push(dest: str, vault_file: str, password: str) -> None:
    """Encrypt vault contents and write them to DEST."""
    vault = get_vault(vault_file, password)
    dest_path = Path(dest)
    try:
        push_to_file(vault, dest_path, password)
        click.echo(f"Vault pushed to {dest_path}")
    except Exception as exc:  # pragma: no cover
        raise click.ClickException(str(exc)) from exc


@sync_group.command("pull")
@click.argument("src", type=click.Path(exists=True, dir_okay=False, readable=True))
@click.option(
    "--vault-file",
    default=".envault",
    show_default=True,
    help="Path to the local vault file.",
)
@click.option(
    "--no-overwrite",
    is_flag=True,
    default=False,
    help="Skip keys that already exist in the local vault.",
)
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False)
def sync_pull(src: str, vault_file: str, no_overwrite: bool, password: str) -> None:
    """Decrypt SRC and merge its contents into the local vault."""
    vault = get_vault(vault_file, password)
    try:
        written = pull_from_file(vault, Path(src), password, overwrite=not no_overwrite)
        click.echo(f"Pulled {written} key(s) into vault.")
    except SyncError as exc:
        raise click.ClickException(str(exc)) from exc
