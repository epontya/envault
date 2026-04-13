"""CLI commands for managing vault webhooks."""
from __future__ import annotations

from pathlib import Path

import click

from envault.webhook import WebhookStore, WebhookError


def _ws(vault_file: str) -> WebhookStore:
    store_path = Path(vault_file).with_suffix(".webhooks.json")
    return WebhookStore(store_path)


@click.group("webhook")
def webhook_group() -> None:
    """Manage webhook notifications for vault events."""


@webhook_group.command("add")
@click.argument("url")
@click.option("--event", "events", multiple=True, help="Event filter (repeatable). Omit for all events.")
@click.option("--secret", default=None, help="Shared secret sent in X-Envault-Secret header.")
@click.option("--vault", "vault_file", required=True, envvar="ENVAULT_VAULT", help="Path to vault file.")
def webhook_add(url: str, events: tuple, secret: str, vault_file: str) -> None:
    """Register a webhook URL."""
    try:
        entry = _ws(vault_file).add(url, list(events) if events else [], secret)
        scope = ", ".join(entry.events) if entry.events else "all events"
        click.echo(f"Registered webhook: {url} ({scope})")
    except WebhookError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@webhook_group.command("remove")
@click.argument("url")
@click.option("--vault", "vault_file", required=True, envvar="ENVAULT_VAULT", help="Path to vault file.")
def webhook_remove(url: str, vault_file: str) -> None:
    """Unregister a webhook URL."""
    removed = _ws(vault_file).remove(url)
    if removed:
        click.echo(f"Removed webhook: {url}")
    else:
        click.echo(f"Webhook not found: {url}", err=True)
        raise SystemExit(1)


@webhook_group.command("list")
@click.option("--vault", "vault_file", required=True, envvar="ENVAULT_VAULT", help="Path to vault file.")
def webhook_list(vault_file: str) -> None:
    """List registered webhooks."""
    hooks = _ws(vault_file).list()
    if not hooks:
        click.echo("No webhooks registered.")
        return
    for h in hooks:
        scope = ", ".join(h.events) if h.events else "all"
        secret_hint = " [secret]" if h.secret else ""
        click.echo(f"  {h.url}  events={scope}{secret_hint}")


@webhook_group.command("fire")
@click.argument("event")
@click.option("--vault", "vault_file", required=True, envvar="ENVAULT_VAULT", help="Path to vault file.")
def webhook_fire(event: str, vault_file: str) -> None:
    """Manually fire a test event to all matching webhooks."""
    failed = _ws(vault_file).fire(event, {"source": "manual", "vault": vault_file})
    if failed:
        click.echo(f"Failed to deliver to: {', '.join(failed)}", err=True)
        raise SystemExit(1)
    click.echo(f"Event '{event}' dispatched successfully.")
