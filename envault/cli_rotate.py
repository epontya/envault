"""CLI commands for vault key rotation."""

from __future__ import annotations

import click

from envault.cli import get_vault
from envault.rotate import RotationError, rotate_vault_password
from envault.vault import VaultNotFoundError


@click.group("rotate")
def rotate_group() -> None:  # pragma: no cover
    """Rotate the master password of a vault."""


@rotate_group.command("run")
@click.option(
    "--vault",
    "vault_path",
    default=".envault",
    show_default=True,
    help="Path to the vault file.",
)
@click.option(
    "--old-password",
    prompt=True,
    hide_input=True,
    help="Current vault password.",
)
@click.option(
    "--new-password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
    help="New vault password.",
)
def rotate_run(vault_path: str, old_password: str, new_password: str) -> None:
    """Re-encrypt the vault under a new password."""
    from pathlib import Path

    path = Path(vault_path)
    try:
        count = rotate_vault_password(path, old_password, new_password)
    except VaultNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    except RotationError as exc:
        raise click.ClickException(str(exc)) from exc
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Rotated password for {count} entr{'y' if count == 1 else 'ies'} in '{vault_path}'.")
