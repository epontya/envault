"""CLI commands for managing vault lookup chains."""
from __future__ import annotations

from pathlib import Path

import click

from envault.cli import get_vault
from envault.env_chain import (
    ChainError,
    add_vault,
    list_chain,
    remove_vault,
    resolve_all,
    resolve_key,
)


@click.group("chain")
def chain_group() -> None:
    """Manage ordered vault lookup chains."""


@chain_group.command("add")
@click.argument("vault_file", envvar="ENVAULT_VAULT")
@click.argument("linked_vault")
def chain_add(vault_file: str, linked_vault: str) -> None:
    """Append LINKED_VAULT to the lookup chain of VAULT_FILE."""
    try:
        chain = add_vault(Path(vault_file), Path(linked_vault))
        click.echo(f"Chain updated ({len(chain)} vaults):")
        for i, vp in enumerate(chain, 1):
            click.echo(f"  {i}. {vp}")
    except ChainError as exc:
        raise click.ClickException(str(exc))


@chain_group.command("remove")
@click.argument("vault_file", envvar="ENVAULT_VAULT")
@click.argument("linked_vault")
def chain_remove(vault_file: str, linked_vault: str) -> None:
    """Remove LINKED_VAULT from the chain."""
    removed = remove_vault(Path(vault_file), Path(linked_vault))
    if removed:
        click.echo(f"Removed {linked_vault} from chain.")
    else:
        raise click.ClickException(f"{linked_vault} is not in the chain.")


@chain_group.command("list")
@click.argument("vault_file", envvar="ENVAULT_VAULT")
def chain_list(vault_file: str) -> None:
    """List all vaults in the lookup chain."""
    chain = list_chain(Path(vault_file))
    if not chain:
        click.echo("No vaults in chain.")
        return
    for i, vp in enumerate(chain, 1):
        click.echo(f"{i}. {vp}")


@chain_group.command("get")
@click.argument("vault_file", envvar="ENVAULT_VAULT")
@click.argument("key")
@click.password_option("--password", "-p", prompt="Vault password")
def chain_get(vault_file: str, key: str, password: str) -> None:
    """Resolve KEY by searching the chain; print the first match."""
    value = resolve_key(Path(vault_file), key, password)
    if value is None:
        raise click.ClickException(f"Key '{key}' not found in chain.")
    click.echo(value)


@chain_group.command("resolve")
@click.argument("vault_file", envvar="ENVAULT_VAULT")
@click.password_option("--password", "-p", prompt="Vault password")
def chain_resolve(vault_file: str, password: str) -> None:
    """Print all resolved key=value pairs across the chain."""
    merged = resolve_all(Path(vault_file), password)
    if not merged:
        click.echo("No entries found.")
        return
    for k, v in sorted(merged.items()):
        click.echo(f"{k}={v}")
