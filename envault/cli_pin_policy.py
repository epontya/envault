"""CLI commands for managing vault PIN policies."""
from __future__ import annotations

from pathlib import Path

import click

from envault.env_pin_policy import (
    PinPolicyError,
    enforce_policy,
    get_policy,
    remove_policy,
    set_policy,
)


@click.group("pin-policy")
def pin_policy_group() -> None:
    """Manage PIN access policies for vaults."""


@pin_policy_group.command("set")
@click.argument("vault_file", type=click.Path())
@click.option("--require/--no-require", default=True, show_default=True)
@click.option("--min-length", default=4, show_default=True, type=int)
@click.option("--max-attempts", default=3, show_default=True, type=int)
def policy_set(
    vault_file: str, require: bool, min_length: int, max_attempts: int
) -> None:
    """Set PIN policy for VAULT_FILE."""
    try:
        policy = set_policy(
            Path(vault_file),
            require_pin=require,
            min_pin_length=min_length,
            max_attempts=max_attempts,
        )
        click.echo(
            f"Policy set: require_pin={policy['require_pin']}, "
            f"min_pin_length={policy['min_pin_length']}, "
            f"max_attempts={policy['max_attempts']}"
        )
    except PinPolicyError as exc:
        raise click.ClickException(str(exc))


@pin_policy_group.command("show")
@click.argument("vault_file", type=click.Path())
def policy_show(vault_file: str) -> None:
    """Show current PIN policy for VAULT_FILE."""
    policy = get_policy(Path(vault_file))
    click.echo(f"require_pin    : {policy['require_pin']}")
    click.echo(f"min_pin_length : {policy['min_pin_length']}")
    click.echo(f"max_attempts   : {policy['max_attempts']}")


@pin_policy_group.command("remove")
@click.argument("vault_file", type=click.Path())
def policy_remove(vault_file: str) -> None:
    """Remove the PIN policy for VAULT_FILE."""
    removed = remove_policy(Path(vault_file))
    if removed:
        click.echo("PIN policy removed.")
    else:
        click.echo("No PIN policy found.")


@pin_policy_group.command("check")
@click.argument("vault_file", type=click.Path())
@click.argument("pin")
def policy_check(vault_file: str, pin: str) -> None:
    """Check whether PIN satisfies the policy for VAULT_FILE."""
    try:
        enforce_policy(Path(vault_file), pin)
        click.echo("PIN satisfies policy.")
    except PinPolicyError as exc:
        raise click.ClickException(str(exc))
