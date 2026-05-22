"""CLI commands for vault cloning."""
from __future__ import annotations

from pathlib import Path

import click

from envault.env_clone import CloneError, clone_vault, clone_vault_file
from envault.vault import VaultNotFoundError


@click.group("clone", help="Clone a vault or selected entries into a new file.")
def clone_group() -> None:  # pragma: no cover
    pass


@clone_group.command("run")
@click.argument("src", type=click.Path(dir_okay=False))
@click.argument("dst", type=click.Path(dir_okay=False))
@click.password_option("-p", "--password", prompt="Vault password")
@click.option("--key", "keys", multiple=True, help="Keys to copy (repeatable).")
@click.option(
    "--overwrite", is_flag=True, default=False, help="Replace destination if it exists."
)
def clone_run(
    src: str,
    dst: str,
    password: str,
    keys: tuple[str, ...],
    overwrite: bool,
) -> None:
    """Clone SRC vault into DST, decrypting and re-encrypting entries."""
    try:
        count = clone_vault(
            Path(src),
            Path(dst),
            password,
            keys=keys if keys else None,
            overwrite=overwrite,
        )
    except (VaultNotFoundError, CloneError) as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"Cloned {count} entr{'y' if count == 1 else 'ies'} → {dst}")


@clone_group.command("raw")
@click.argument("src", type=click.Path(dir_okay=False))
@click.argument("dst", type=click.Path(dir_okay=False))
@click.option(
    "--overwrite", is_flag=True, default=False, help="Replace destination if it exists."
)
def clone_raw(
    src: str,
    dst: str,
    overwrite: bool,
) -> None:
    """Byte-copy SRC vault to DST without decrypting (password unchanged)."""
    try:
        clone_vault_file(Path(src), Path(dst), overwrite=overwrite)
    except (VaultNotFoundError, CloneError) as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"Raw clone complete: {src} → {dst}")
