"""CLI commands for managing vault operation rate limits."""

from __future__ import annotations

from pathlib import Path

import click

from envault.rate_limit import RateLimitError, RateLimitStore


def _rl(vault_file: str) -> RateLimitStore:
    store_path = Path(vault_file).parent / ".envault_rate_limits.json"
    return RateLimitStore(store_path)


@click.group("rate-limit")
def rate_limit_group() -> None:
    """Manage per-operation rate limits."""


@rate_limit_group.command("set")
@click.argument("operation")
@click.option("--max-calls", required=True, type=int, help="Maximum calls allowed in the window.")
@click.option("--window", required=True, type=int, help="Time window in seconds.")
@click.option("--vault", "vault_file", envvar="ENVAULT_VAULT", required=True)
def rate_limit_set(operation: str, max_calls: int, window: int, vault_file: str) -> None:
    """Configure a rate limit for an operation."""
    try:
        _rl(vault_file).configure(operation, max_calls, window)
        click.echo(f"Rate limit set: {operation} → {max_calls} calls / {window}s")
    except RateLimitError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@rate_limit_group.command("get")
@click.argument("operation")
@click.option("--vault", "vault_file", envvar="ENVAULT_VAULT", required=True)
def rate_limit_get(operation: str, vault_file: str) -> None:
    """Show the rate limit configuration for an operation."""
    entry = _rl(vault_file).get(operation)
    if entry is None:
        click.echo(f"No rate limit configured for '{operation}'.")
        raise SystemExit(1)
    click.echo(f"operation : {entry.operation}")
    click.echo(f"max_calls : {entry.max_calls}")
    click.echo(f"window    : {entry.window_seconds}s")


@rate_limit_group.command("remove")
@click.argument("operation")
@click.option("--vault", "vault_file", envvar="ENVAULT_VAULT", required=True)
def rate_limit_remove(operation: str, vault_file: str) -> None:
    """Remove a rate limit for an operation."""
    removed = _rl(vault_file).remove(operation)
    if removed:
        click.echo(f"Rate limit removed for '{operation}'.")
    else:
        click.echo(f"No rate limit found for '{operation}'.")
        raise SystemExit(1)


@rate_limit_group.command("list")
@click.option("--vault", "vault_file", envvar="ENVAULT_VAULT", required=True)
def rate_limit_list(vault_file: str) -> None:
    """List all configured rate limits."""
    rl = _rl(vault_file)
    ops = rl.list_operations()
    if not ops:
        click.echo("No rate limits configured.")
        return
    for op in ops:
        entry = rl.get(op)
        click.echo(f"{op}: {entry.max_calls} calls / {entry.window_seconds}s")
