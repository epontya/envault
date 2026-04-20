"""CLI commands for promoting vault entries between environments."""
from __future__ import annotations

from pathlib import Path

import click

from envault.env_promote import PromoteError, promote_entries
from envault.vault import VaultNotFoundError


@click.group("promote")
def promote_group() -> None:
    """Promote variables from one vault to another."""


@promote_group.command("run")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.argument("dst", type=click.Path(exists=True, path_type=Path))
@click.option("--src-password", prompt=True, hide_input=True, help="Source vault password.")
@click.option("--dst-password", prompt=True, hide_input=True, help="Destination vault password.")
@click.option("-k", "--key", "keys", multiple=True, help="Key(s) to promote (default: all).")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys in destination.")
def promote_run(
    src: Path,
    dst: Path,
    src_password: str,
    dst_password: str,
    keys: tuple[str, ...],
    overwrite: bool,
) -> None:
    """Promote entries from SRC vault into DST vault."""
    try:
        result = promote_entries(
            src,
            dst,
            src_password,
            dst_password,
            keys=list(keys) if keys else None,
            overwrite=overwrite,
        )
    except (VaultNotFoundError, PromoteError) as exc:
        raise click.ClickException(str(exc)) from exc

    if not result:
        click.echo("No entries found in source vault.")
        return

    promoted = [k for k, v in result.items() if v == "promoted"]
    skipped = [k for k, v in result.items() if v == "skipped"]

    for key in promoted:
        click.echo(f"  promoted  {key}")
    for key in skipped:
        click.echo(f"  skipped   {key}  (already exists, use --overwrite to replace)")

    click.echo(f"\nDone: {len(promoted)} promoted, {len(skipped)} skipped.")
