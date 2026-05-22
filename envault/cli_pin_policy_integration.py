"""Integration helpers: gate vault set/get behind PIN policy enforcement."""
from __future__ import annotations

from pathlib import Path

import click

from envault.env_pin_policy import PinPolicyError, enforce_policy, get_policy
from envault.pin import PINError, PINStore
from envault.vault import Vault


def _pin_store(vault_path: Path) -> PINStore:
    return PINStore(vault_path.with_suffix(".pin.json"))


def guarded_vault_get(vault_path: Path, password: str, key: str, pin: str) -> str | None:
    """Get a vault value, enforcing PIN policy before access."""
    policy = get_policy(vault_path)
    if policy["require_pin"]:
        try:
            enforce_policy(vault_path, pin)
        except PinPolicyError as exc:
            raise click.ClickException(f"PIN policy violation: {exc}")
        store = _pin_store(vault_path)
        try:
            store.unlock(pin)
        except PINError as exc:
            raise click.ClickException(f"PIN unlock failed: {exc}")
    vault = Vault(vault_path, password)
    return vault.get(key)


def guarded_vault_set(
    vault_path: Path, password: str, key: str, value: str, pin: str
) -> None:
    """Set a vault value, enforcing PIN policy before write."""
    policy = get_policy(vault_path)
    if policy["require_pin"]:
        try:
            enforce_policy(vault_path, pin)
        except PinPolicyError as exc:
            raise click.ClickException(f"PIN policy violation: {exc}")
        store = _pin_store(vault_path)
        try:
            store.unlock(pin)
        except PINError as exc:
            raise click.ClickException(f"PIN unlock failed: {exc}")
    vault = Vault(vault_path, password)
    vault.set(key, value)


@click.group("pin-policy-ops")
def pin_policy_ops_group() -> None:
    """Vault operations gated by PIN policy."""


@pin_policy_ops_group.command("get")
@click.argument("vault_file", type=click.Path(exists=True))
@click.argument("key")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--pin", default="", help="PIN if policy requires it")
def pg_get(vault_file: str, key: str, password: str, pin: str) -> None:
    """Get KEY from VAULT_FILE, respecting PIN policy."""
    val = guarded_vault_get(Path(vault_file), password, key, pin)
    if val is None:
        raise click.ClickException(f"Key '{key}' not found.")
    click.echo(val)


@pin_policy_ops_group.command("set")
@click.argument("vault_file", type=click.Path())
@click.argument("key")
@click.argument("value")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--pin", default="", help="PIN if policy requires it")
def pg_set(vault_file: str, key: str, value: str, password: str, pin: str) -> None:
    """Set KEY=VALUE in VAULT_FILE, respecting PIN policy."""
    guarded_vault_set(Path(vault_file), password, key, value, pin)
    click.echo(f"Set '{key}'.")
