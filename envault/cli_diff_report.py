"""CLI commands for generating diff reports between vault snapshots or files."""
from __future__ import annotations

import json as _json
import sys
from pathlib import Path

import click

from envault.cli import get_vault
from envault.env_diff_report import build_report, DiffReportError
from envault.snapshot import load_snapshot, SnapshotError


@click.group("diff-report")
def diff_report_group() -> None:
    """Generate structured diff reports between env states."""


@diff_report_group.command("snapshots")
@click.argument("vault_file", type=click.Path(exists=True))
@click.argument("snap_a")
@click.argument("snap_b")
@click.option("--snap-dir", default=None, help="Directory containing snapshots.")
@click.option("--show-values", is_flag=True, default=False, help="Show plaintext values.")
@click.option("--redact", is_flag=True, default=True, help="Redact values in output.")
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text")
@click.option("--include-unchanged", is_flag=True, default=False)
def diff_report_snapshots(
    vault_file: str,
    snap_a: str,
    snap_b: str,
    snap_dir: str | None,
    show_values: bool,
    redact: bool,
    fmt: str,
    include_unchanged: bool,
) -> None:
    """Diff two named snapshots of VAULT_FILE."""
    vpath = Path(vault_file)
    try:
        data_a = load_snapshot(vpath, snap_a, snap_dir=Path(snap_dir) if snap_dir else None)
        data_b = load_snapshot(vpath, snap_b, snap_dir=Path(snap_dir) if snap_dir else None)
    except SnapshotError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    report = build_report(data_a, data_b, include_unchanged=include_unchanged)

    if fmt == "json":
        click.echo(_json.dumps([e.to_dict() for e in report.entries], indent=2))
    else:
        click.echo(f"Diff: {snap_a} -> {snap_b}")
        click.echo(f"Summary: {report.summary()}")
        click.echo(report.to_text(show_values=show_values, redact=redact))

    sys.exit(0 if not report.has_differences() else 1)


@diff_report_group.command("live")
@click.argument("vault_file", type=click.Path(exists=True))
@click.argument("snap_name")
@click.argument("password")
@click.option("--snap-dir", default=None)
@click.option("--show-values", is_flag=True, default=False)
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text")
@click.option("--include-unchanged", is_flag=True, default=False)
def diff_report_live(
    vault_file: str,
    snap_name: str,
    password: str,
    snap_dir: str | None,
    show_values: bool,
    fmt: str,
    include_unchanged: bool,
) -> None:
    """Diff the live vault against a named snapshot."""
    vpath = Path(vault_file)
    vault = get_vault(vpath, password)
    live_data: dict = {k: vault.get(k) or "" for k in (vault.list() if hasattr(vault, "list") else [])}

    try:
        snap_data = load_snapshot(vpath, snap_name, snap_dir=Path(snap_dir) if snap_dir else None)
    except SnapshotError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    report = build_report(snap_data, live_data, include_unchanged=include_unchanged)

    if fmt == "json":
        click.echo(_json.dumps([e.to_dict() for e in report.entries], indent=2))
    else:
        click.echo(f"Diff: {snap_name} -> live")
        click.echo(f"Summary: {report.summary()}")
        click.echo(report.to_text(show_values=show_values, redact=True))

    sys.exit(0 if not report.has_differences() else 1)
