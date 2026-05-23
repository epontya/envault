"""cli_preview.py – CLI commands for vault entry preview."""
from __future__ import annotations

import click

from envault.cli import get_vault
from envault.env_preview import PreviewError, build_preview, format_table


@click.group("preview")
def preview_group() -> None:
    """Preview vault entries with optional redaction."""


@preview_group.command("show")
@click.option("--vault", "vault_path", required=True, help="Path to vault file.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option("--reveal", is_flag=True, default=False, help="Show sensitive values.")
@click.option(
    "--pattern",
    "extra_patterns",
    multiple=True,
    help="Extra glob patterns to treat as sensitive.",
)
@click.option(
    "--max-length",
    default=60,
    show_default=True,
    help="Max display length before truncation.",
)
def preview_show(
    vault_path: str,
    password: str,
    reveal: bool,
    extra_patterns: tuple,
    max_length: int,
) -> None:
    """Display a formatted preview of all vault entries."""
    vault = get_vault(vault_path, password)
    data = vault.all()
    try:
        entries = build_preview(
            data,
            reveal=reveal,
            extra_patterns=list(extra_patterns),
            max_value_length=max_length,
        )
    except PreviewError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(format_table(entries))


@preview_group.command("key")
@click.argument("key")
@click.option("--vault", "vault_path", required=True, help="Path to vault file.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option("--reveal", is_flag=True, default=False, help="Show sensitive value.")
def preview_key(key: str, vault_path: str, password: str, reveal: bool) -> None:
    """Preview a single vault entry by KEY."""
    vault = get_vault(vault_path, password)
    data = vault.all()
    if key not in data:
        raise click.ClickException(f"Key '{key}' not found in vault.")
    entries = build_preview({key: data[key]}, reveal=reveal)
    click.echo(format_table(entries))
