"""cli_mask.py – CLI commands for displaying masked vault values."""
from __future__ import annotations

import click

from envault.cli import get_vault
from envault.env_mask import DEFAULT_MASK, is_sensitive_key, mask_dict, mask_value


@click.group("mask", help="Display vault values with sensitive fields masked.")
def mask_group() -> None:
    pass


@mask_group.command("show")
@click.argument("vault_path")
@click.argument("password")
@click.option("--reveal", default=0, show_default=True, help="Reveal last N chars of masked values.")
@click.option("--mask-char", default=DEFAULT_MASK, show_default=True, help="Mask string to use.")
def mask_show(vault_path: str, password: str, reveal: int, mask_char: str) -> None:
    """Print all vault entries, masking sensitive values."""
    vault = get_vault(vault_path, password)
    data = {k: vault.get(k) or "" for k in vault.keys()}
    masked = mask_dict(data, mask=mask_char, reveal_chars=reveal)
    if not masked:
        click.echo("(empty vault)")
        return
    for key, value in sorted(masked.items()):
        click.echo(f"{key}={value}")


@mask_group.command("check")
@click.argument("key")
def mask_check(key: str) -> None:
    """Check whether KEY would be considered sensitive."""
    if is_sensitive_key(key):
        click.echo(f"{key}: sensitive")
    else:
        click.echo(f"{key}: not sensitive")


@mask_group.command("value")
@click.argument("value")
@click.option("--reveal", default=0, show_default=True, help="Reveal last N chars.")
@click.option("--mask-char", default=DEFAULT_MASK, show_default=True, help="Mask string to use.")
def mask_value_cmd(value: str, reveal: int, mask_char: str) -> None:
    """Mask a single VALUE and print the result."""
    click.echo(mask_value(value, mask=mask_char, reveal_chars=reveal))
