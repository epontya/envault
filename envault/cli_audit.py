"""CLI commands for viewing the envault audit log."""

from __future__ import annotations

import click

from envault.audit import AuditLog, DEFAULT_AUDIT_FILE


@click.group("audit")
def audit_group() -> None:
    """View and manage the envault audit log."""


@audit_group.command("log")
@click.option(
    "--limit",
    "-n",
    default=20,
    show_default=True,
    help="Number of recent entries to show.",
)
@click.option(
    "--log-file",
    default=str(DEFAULT_AUDIT_FILE),
    show_default=True,
    help="Path to the audit log file.",
)
def audit_log(limit: int, log_file: str) -> None:
    """Display recent audit log entries."""
    al = AuditLog(log_file)
    entries = al.read(limit=limit)
    if not entries:
        click.echo("No audit entries found.")
        return
    for e in entries:
        status = "OK" if e.get("success") else "FAIL"
        key_part = f"  key={e['key']}" if e.get("key") else ""
        profile_part = f"  profile={e['profile']}" if e.get("profile") else ""
        click.echo(
            f"[{e['timestamp']}] {status} {e['action']}"
            f"  vault={e['vault']}{key_part}{profile_part}"
            f"  user={e.get('user', 'unknown')}"
        )


@audit_group.command("clear")
@click.option(
    "--log-file",
    default=str(DEFAULT_AUDIT_FILE),
    show_default=True,
    help="Path to the audit log file.",
)
@click.confirmation_option(prompt="Clear the entire audit log?")
def audit_clear(log_file: str) -> None:
    """Erase all entries from the audit log."""
    AuditLog(log_file).clear()
    click.echo("Audit log cleared.")
