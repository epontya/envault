"""Command-line interface for envault."""

import sys
import click
from pathlib import Path

from envault.vault import Vault, VaultNotFoundError


DEFAULT_VAULT_PATH = Path.home() / ".envault" / "default.vault"


def get_vault(vault_path: Path, password: str) -> Vault:
    """Open or create a vault at the given path."""
    vault_path.parent.mkdir(parents=True, exist_ok=True)
    return Vault(str(vault_path), password)


@click.group()
@click.version_option()
def cli():
    """envault — securely store and sync environment variables."""
    pass


@cli.command("set")
@click.argument("key")
@click.argument("value")
@click.option("--vault", "vault_path", default=str(DEFAULT_VAULT_PATH), show_default=True, help="Path to vault file.")
@click.password_option("--password", prompt="Vault password", help="Vault encryption password.")
def set_cmd(key, value, vault_path, password):
    """Set KEY to VALUE in the vault."""
    vault = get_vault(Path(vault_path), password)
    vault.set(key, value)
    click.echo(f"✓ Set '{key}' in vault.")


@cli.command("get")
@click.argument("key")
@click.option("--vault", "vault_path", default=str(DEFAULT_VAULT_PATH), show_default=True, help="Path to vault file.")
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False, help="Vault encryption password.")
def get_cmd(key, vault_path, password):
    """Get the value of KEY from the vault."""
    try:
        vault = get_vault(Path(vault_path), password)
    except VaultNotFoundError:
        click.echo(f"Error: vault not found at '{vault_path}'.", err=True)
        sys.exit(1)

    value = vault.get(key)
    if value is None:
        click.echo(f"Error: key '{key}' not found in vault.", err=True)
        sys.exit(1)
    click.echo(value)


@cli.command("delete")
@click.argument("key")
@click.option("--vault", "vault_path", default=str(DEFAULT_VAULT_PATH), show_default=True, help="Path to vault file.")
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False, help="Vault encryption password.")
def delete_cmd(key, vault_path, password):
    """Delete KEY from the vault."""
    vault = get_vault(Path(vault_path), password)
    removed = vault.delete(key)
    if removed:
        click.echo(f"✓ Deleted '{key}' from vault.")
    else:
        click.echo(f"Key '{key}' not found in vault.", err=True)
        sys.exit(1)


@cli.command("list")
@click.option("--vault", "vault_path", default=str(DEFAULT_VAULT_PATH), show_default=True, help="Path to vault file.")
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False, help="Vault encryption password.")
def list_cmd(vault_path, password):
    """List all keys stored in the vault."""
    vault = get_vault(Path(vault_path), password)
    keys = vault.keys()
    if not keys:
        click.echo("Vault is empty.")
    else:
        for key in sorted(keys):
            click.echo(key)


if __name__ == "__main__":
    cli()
