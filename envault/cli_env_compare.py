"""CLI commands for comparing vault contents against .env files or the environment."""

from __future__ import annotations

from pathlib import Path

import click

from envault.cli import get_vault
from envault.env_compare import CompareError, compare_with_dotenv, compare_with_env


@click.group("compare")
def compare_group() -> None:
    """Compare vault entries against external sources."""


@compare_group.command("dotenv")
@click.argument("dotenv_path", type=click.Path(exists=True, dir_okay=False))
@click.option("--vault", "vault_path", default=".envault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
@click.option("--key", "keys", multiple=True, help="Limit comparison to these keys.")
@click.option("--only-diff", is_flag=True, help="Show only differing entries.")
def compare_dotenv(
    dotenv_path: str,
    vault_path: str,
    password: str,
    keys: tuple,
    only_diff: bool,
) -> None:
    """Compare vault entries against a .env file."""
    vault = get_vault(vault_path, password)
    try:
        result = compare_with_dotenv(
            vault, Path(dotenv_path), list(keys) if keys else None
        )
    except CompareError as exc:
        raise click.ClickException(str(exc)) from exc

    if only_diff and not result.has_differences():
        click.echo("No differences found.")
        return

    click.echo(result.summary())
    if result.has_differences():
        raise SystemExit(1)


@compare_group.command("env")
@click.option("--vault", "vault_path", default=".envault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
@click.option("--key", "keys", multiple=True, help="Limit comparison to these keys.")
@click.option("--only-diff", is_flag=True, help="Show only differing entries.")
def compare_env(
    vault_path: str,
    password: str,
    keys: tuple,
    only_diff: bool,
) -> None:
    """Compare vault entries against the current process environment."""
    vault = get_vault(vault_path, password)
    result = compare_with_env(vault, list(keys) if keys else None)

    if only_diff and not result.has_differences():
        click.echo("No differences found.")
        return

    click.echo(result.summary())
    if result.has_differences():
        raise SystemExit(1)
