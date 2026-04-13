"""CLI commands for managing vault password policies."""
from __future__ import annotations

from pathlib import Path

import click

from envault.cli import get_vault
from envault.policy import (
    PolicyConfig,
    PolicyError,
    load_policy,
    save_policy,
    check_value,
)


@click.group("policy")
def policy_group() -> None:
    """Manage value policies for a vault."""


@policy_group.command("set")
@click.option("--vault", "vault_path", required=True, type=click.Path(), help="Path to vault file.")
@click.option("--min-length", type=int, default=None)
@click.option("--max-length", type=int, default=None)
@click.option("--require-uppercase", is_flag=True, default=None)
@click.option("--require-lowercase", is_flag=True, default=None)
@click.option("--require-digit", is_flag=True, default=None)
@click.option("--require-special", is_flag=True, default=None)
def policy_set(
    vault_path: str,
    min_length,
    max_length,
    require_uppercase,
    require_lowercase,
    require_digit,
    require_special,
) -> None:
    """Set policy rules for a vault."""
    p = Path(vault_path)
    cfg = load_policy(p)
    if min_length is not None:
        cfg.min_length = min_length
    if max_length is not None:
        cfg.max_length = max_length
    if require_uppercase:
        cfg.require_uppercase = True
    if require_lowercase:
        cfg.require_lowercase = True
    if require_digit:
        cfg.require_digit = True
    if require_special:
        cfg.require_special = True
    save_policy(p, cfg)
    click.echo("Policy updated.")


@policy_group.command("show")
@click.option("--vault", "vault_path", required=True, type=click.Path())
def policy_show(vault_path: str) -> None:
    """Show current policy for a vault."""
    cfg = load_policy(Path(vault_path))
    for k, v in cfg.to_dict().items():
        click.echo(f"{k}: {v}")


@policy_group.command("check")
@click.option("--vault", "vault_path", required=True, type=click.Path())
@click.argument("value")
def policy_check(vault_path: str, value: str) -> None:
    """Check VALUE against the vault policy."""
    cfg = load_policy(Path(vault_path))
    violations = check_value(value, cfg)
    if not violations:
        click.echo("OK — value satisfies all policy rules.")
        return
    for v in violations:
        click.echo(f"[{v.rule}] {v.message}", err=True)
    raise SystemExit(1)
