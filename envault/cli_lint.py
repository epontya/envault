"""CLI commands for linting vault entries."""

from __future__ import annotations

import click

from envault.cli import get_vault
from envault.lint import lint_vault


@click.group("lint")
def lint_group() -> None:
    """Check vault entries for common issues."""


@lint_group.command("run")
@click.option("--vault-file", "vault_path", default=".envault",
              show_default=True, help="Path to the vault file.")
@click.option("--password", prompt=True, hide_input=True,
              help="Vault password.")
@click.option("--strict", is_flag=True, default=False,
              help="Exit non-zero if any warnings are found (in addition to errors).")
def lint_run(vault_path: str, password: str, strict: bool) -> None:
    """Run linter against all entries in the vault."""
    vault = get_vault(vault_path, password)
    result = lint_vault(vault, password)

    if not result.issues:
        click.echo(click.style("No issues found.", fg="green"))
        return

    for issue in result.issues:
        colour = "red" if issue.severity == "error" else "yellow"
        prefix = issue.severity.upper()
        click.echo(click.style(f"[{prefix}] {issue.message}", fg=colour))

    click.echo(f"\n{result.summary()}")

    if result.has_errors or (strict and result.has_warnings):
        raise SystemExit(1)
