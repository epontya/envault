"""CLI commands for copying / moving entries between vaults."""

from __future__ import annotations

from pathlib import Path

import click

from envault.copy import CopyError, copy_entries, move_entries
from envault.vault import VaultNotFoundError


@click.group("copy", help="Copy or move entries between vaults.")
def copy_group() -> None:  # pragma: no cover
    pass


@copy_group.command("run")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.argument("dst", type=click.Path(path_type=Path))
@click.option("--src-password", prompt=True, hide_input=True, envvar="ENVAULT_SRC_PASSWORD")
@click.option("--dst-password", prompt=True, hide_input=True, envvar="ENVAULT_DST_PASSWORD")
@click.option("--key", "keys", multiple=True, help="Key(s) to copy (default: all).")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys in dst.")
@click.option("--move", "do_move", is_flag=True, default=False, help="Delete keys from src after copying.")
def copy_run(
    src: Path,
    dst: Path,
    src_password: str,
    dst_password: str,
    keys: tuple,
    overwrite: bool,
    do_move: bool,
) -> None:
    """Copy (or move) entries from SRC vault to DST vault.

    When --move is specified, entries are deleted from SRC after a
    successful copy.  Use --key to restrict the operation to specific
    keys; omitting --key copies/moves all entries.  Pass --overwrite to
    allow replacing keys that already exist in DST.
    """
    selected = list(keys) if keys else None
    try:
        if do_move:
            count = move_entries(src, src_password, dst, dst_password, selected, overwrite)
            verb = "Moved"
        else:
            count = copy_entries(src, src_password, dst, dst_password, selected, overwrite)
            verb = "Copied"
    except VaultNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    except CopyError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"{verb} {count} entr{'y' if count == 1 else 'ies'} to {dst}.")
