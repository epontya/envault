"""CLI commands for managing vault quotas."""

from __future__ import annotations

from pathlib import Path

import click

from envault.quota import QuotaConfig, QuotaError


def _qc(vault_file: str) -> QuotaConfig:
    quota_path = Path(vault_file).with_suffix(".quota.json")
    return QuotaConfig(quota_path)


@click.group("quota")
def quota_group() -> None:
    """Manage per-vault entry and size quotas."""


@quota_group.command("set")
@click.option("--vault", required=True, help="Path to the vault file.")
@click.option("--max-entries", type=int, default=None, help="Maximum number of entries.")
@click.option("--max-value-bytes", type=int, default=None, help="Maximum bytes per value.")
@click.option("--max-total-bytes", type=int, default=None, help="Maximum total bytes across all values.")
def quota_set(vault: str, max_entries: int, max_value_bytes: int, max_total_bytes: int) -> None:
    """Set quota limits for a vault."""
    if all(v is None for v in (max_entries, max_value_bytes, max_total_bytes)):
        raise click.UsageError("Specify at least one limit option.")
    qc = _qc(vault)
    try:
        qc.set_limit(
            max_entries=max_entries,
            max_value_bytes=max_value_bytes,
            max_total_bytes=max_total_bytes,
        )
    except QuotaError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo("Quota updated.")


@quota_group.command("get")
@click.option("--vault", required=True, help="Path to the vault file.")
def quota_get(vault: str) -> None:
    """Show current quota limits for a vault."""
    qc = _qc(vault)
    limits = qc.get_limits()
    click.echo(f"max_entries      : {limits['max_entries']}")
    click.echo(f"max_value_bytes  : {limits['max_value_bytes']}")
    click.echo(f"max_total_bytes  : {limits['max_total_bytes']}")


@quota_group.command("reset")
@click.option("--vault", required=True, help="Path to the vault file.")
def quota_reset(vault: str) -> None:
    """Reset quota limits to defaults for a vault."""
    _qc(vault).reset()
    click.echo("Quota reset to defaults.")
