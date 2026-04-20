"""CLI commands for managing and running vault entry validation rules."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from envault.cli import get_vault
from envault.env_validate import (
    ValidationError,
    add_rule,
    load_rules,
    remove_rule,
    validate_entries,
)


@click.group("validate", help="Manage and run entry validation rules.")
def validate_group() -> None:
    pass


@validate_group.command("add")
@click.option("--vault", "vault_path", required=True, type=click.Path(), help="Path to vault file.")
@click.option("--password", prompt=True, hide_input=True)
@click.argument("key")
@click.argument("rule_type")
@click.argument("rule_value")
def validate_add(vault_path: str, password: str, key: str, rule_type: str, rule_value: str) -> None:
    """Add a validation rule for KEY.\n\nRULE_TYPE: type | regex | nonempty\nRULE_VALUE: the constraint value (e.g. 'int', '^[A-Z]+$', 'true')."""
    vp = Path(vault_path)
    vault = get_vault(vp, password)
    if vault.get(key) is None:
        click.echo(f"Warning: key '{key}' not currently in vault.", err=True)
    try:
        add_rule(vp, key, rule_type, rule_value)
    except ValidationError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
    click.echo(f"Rule '{rule_type}={rule_value}' added for '{key}'.")


@validate_group.command("remove")
@click.option("--vault", "vault_path", required=True, type=click.Path())
@click.argument("key")
def validate_remove(vault_path: str, key: str) -> None:
    """Remove all validation rules for KEY."""
    vp = Path(vault_path)
    removed = remove_rule(vp, key)
    if removed:
        click.echo(f"Rules for '{key}' removed.")
    else:
        click.echo(f"No rules found for '{key}'.", err=True)
        sys.exit(1)


@validate_group.command("list")
@click.option("--vault", "vault_path", required=True, type=click.Path())
def validate_list(vault_path: str) -> None:
    """List all validation rules for the vault."""
    rules = load_rules(Path(vault_path))
    if not rules:
        click.echo("No validation rules defined.")
        return
    for key, key_rules in sorted(rules.items()):
        for rule_type, rule_value in key_rules.items():
            click.echo(f"{key}  {rule_type}={rule_value}")


@validate_group.command("run")
@click.option("--vault", "vault_path", required=True, type=click.Path())
@click.option("--password", prompt=True, hide_input=True)
def validate_run(vault_path: str, password: str) -> None:
    """Run all validation rules against the current vault entries."""
    vp = Path(vault_path)
    vault = get_vault(vp, password)
    entries = {k: vault.get(k) for k in vault.keys()}  # type: ignore[attr-defined]
    result = validate_entries(entries, vp)
    if not result.issues:
        click.echo("All validations passed.")
        return
    for issue in result.issues:
        prefix = "ERROR" if issue.severity == "error" else "WARN "
        click.echo(f"[{prefix}] {issue.key}: {issue.message}")
    click.echo(result.summary())
    if result.has_errors():
        sys.exit(1)
