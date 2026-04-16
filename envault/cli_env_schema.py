"""CLI commands for vault schema management."""
from __future__ import annotations

from pathlib import Path

import click

from envault.env_schema import FieldRule, SchemaError, add_rule, load_schema, remove_rule, validate
from envault.vault import Vault


@click.group("schema")
def schema_group() -> None:
    """Manage key validation schemas for a vault."""


@schema_group.command("add")
@click.argument("vault_file")
@click.argument("key")
@click.option("--required", is_flag=True, default=False)
@click.option("--pattern", default=None)
@click.option("--min-length", "min_length", default=0, type=int)
@click.option("--max-length", "max_length", default=0, type=int)
def schema_add(vault_file, key, required, pattern, min_length, max_length):
    """Add or update a schema rule for KEY."""
    rule = FieldRule(required=required, pattern=pattern, min_length=min_length, max_length=max_length)
    add_rule(Path(vault_file), key, rule)
    click.echo(f"Schema rule added for '{key}'.")


@schema_group.command("remove")
@click.argument("vault_file")
@click.argument("key")
def schema_remove(vault_file, key):
    """Remove schema rule for KEY."""
    removed = remove_rule(Path(vault_file), key)
    if removed:
        click.echo(f"Schema rule for '{key}' removed.")
    else:
        click.echo(f"No schema rule found for '{key}'.", err=True)
        raise SystemExit(1)


@schema_group.command("list")
@click.argument("vault_file")
def schema_list(vault_file):
    """List all schema rules."""
    schema = load_schema(Path(vault_file))
    if not schema:
        click.echo("No schema rules defined.")
        return
    for key, rule in sorted(schema.items()):
        parts = [f"required={rule.required}"]
        if rule.pattern:
            parts.append(f"pattern={rule.pattern}")
        if rule.min_length:
            parts.append(f"min_length={rule.min_length}")
        if rule.max_length:
            parts.append(f"max_length={rule.max_length}")
        click.echo(f"{key}: {', '.join(parts)}")


@schema_group.command("validate")
@click.argument("vault_file")
@click.argument("password")
def schema_validate(vault_file, password):
    """Validate vault entries against defined schema."""
    vault = Vault(Path(vault_file), password)
    entries = {k: vault.get(k) for k in vault.list()}
    violations = validate(Path(vault_file), entries)
    if not violations:
        click.echo("All entries are valid.")
        return
    for v in violations:
        click.echo(f"  [{v.key}] {v.message}", err=True)
    raise SystemExit(1)
