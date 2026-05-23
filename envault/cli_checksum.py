"""CLI commands for vault checksum management."""

from __future__ import annotations

from pathlib import Path

import click

from envault.cli import get_vault
from envault.env_checksum import (
    ChecksumError,
    load_checksum,
    remove_checksum,
    save_checksum,
    verify_checksum,
)


@click.group("checksum")
def checksum_group() -> None:
    """Manage vault integrity checksums."""


@checksum_group.command("save")
@click.option("--vault", "vault_file", required=True, help="Path to the vault file.")
@click.option("--password", prompt=True, hide_input=True)
def checksum_save(vault_file: str, password: str) -> None:
    """Compute and save a checksum for the vault."""
    vault = get_vault(vault_file, password)
    data = {k: vault.get(k) for k in vault.list()}
    digest = save_checksum(Path(vault_file), data)
    click.echo(f"Checksum saved: {digest}")


@checksum_group.command("verify")
@click.option("--vault", "vault_file", required=True, help="Path to the vault file.")
@click.option("--password", prompt=True, hide_input=True)
def checksum_verify(vault_file: str, password: str) -> None:
    """Verify the vault matches its saved checksum."""
    vault = get_vault(vault_file, password)
    data = {k: vault.get(k) for k in vault.list()}
    try:
        ok = verify_checksum(Path(vault_file), data)
    except ChecksumError as exc:
        raise click.ClickException(str(exc)) from exc
    if ok:
        click.echo("Checksum OK — vault has not been tampered with.")
    else:
        click.echo("Checksum MISMATCH — vault contents may have changed!", err=True)
        raise SystemExit(1)


@checksum_group.command("show")
@click.option("--vault", "vault_file", required=True, help="Path to the vault file.")
def checksum_show(vault_file: str) -> None:
    """Display the stored checksum for a vault."""
    digest = load_checksum(Path(vault_file))
    if digest is None:
        raise click.ClickException("No checksum file found for this vault.")
    click.echo(digest)


@checksum_group.command("remove")
@click.option("--vault", "vault_file", required=True, help="Path to the vault file.")
def checksum_remove(vault_file: str) -> None:
    """Remove the checksum file for a vault."""
    removed = remove_checksum(Path(vault_file))
    if removed:
        click.echo("Checksum file removed.")
    else:
        click.echo("No checksum file found; nothing to remove.")
