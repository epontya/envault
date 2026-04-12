"""CLI commands for managing vault key ACLs."""
from __future__ import annotations

from pathlib import Path

import click

from envault.acl import ACLError, ACLStore


def _store(vault_file: str) -> ACLStore:
    acl_path = Path(vault_file).parent / ".envault_acl.json"
    return ACLStore(acl_path)


@click.group("acl")
def acl_group() -> None:
    """Manage access control lists for vault keys."""


@acl_group.command("grant")
@click.option("--vault", required=True, envvar="ENVAULT_FILE", help="Vault file path.")
@click.argument("key")
@click.argument("role")
@click.argument("permission", type=click.Choice(["read", "write"]))
def acl_grant(vault: str, key: str, role: str, permission: str) -> None:
    """Grant ROLE the PERMISSION on KEY."""
    try:
        _store(vault).grant(key, role, permission)
        click.echo(f"Granted '{permission}' on '{key}' to role '{role}'.")
    except ACLError as exc:
        raise click.ClickException(str(exc)) from exc


@acl_group.command("revoke")
@click.option("--vault", required=True, envvar="ENVAULT_FILE", help="Vault file path.")
@click.argument("key")
@click.argument("role")
@click.argument("permission", type=click.Choice(["read", "write"]))
def acl_revoke(vault: str, key: str, role: str, permission: str) -> None:
    """Revoke ROLE's PERMISSION on KEY."""
    removed = _store(vault).revoke(key, role, permission)
    if removed:
        click.echo(f"Revoked '{permission}' on '{key}' from role '{role}'.")
    else:
        click.echo(f"No matching ACL entry found.", err=True)
        raise SystemExit(1)


@acl_group.command("check")
@click.option("--vault", required=True, envvar="ENVAULT_FILE", help="Vault file path.")
@click.argument("key")
@click.argument("role")
@click.argument("permission", type=click.Choice(["read", "write"]))
def acl_check(vault: str, key: str, role: str, permission: str) -> None:
    """Check whether ROLE has PERMISSION on KEY (exits 0 if yes, 1 if no)."""
    allowed = _store(vault).can(key, role, permission)
    if allowed:
        click.echo(f"ALLOWED: '{role}' can '{permission}' '{key}'.")
    else:
        click.echo(f"DENIED: '{role}' cannot '{permission}' '{key}'.")
        raise SystemExit(1)


@acl_group.command("list")
@click.option("--vault", required=True, envvar="ENVAULT_FILE", help="Vault file path.")
@click.argument("key")
def acl_list(vault: str, key: str) -> None:
    """List all roles and permissions for KEY."""
    roles = _store(vault).roles_for_key(key)
    if not roles:
        click.echo(f"No ACL entries for '{key}'.")
        return
    for role, perms in sorted(roles.items()):
        click.echo(f"  {role}: {', '.join(sorted(perms))}")
