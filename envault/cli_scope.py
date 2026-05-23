"""CLI commands for env-scope management."""

from __future__ import annotations

import click

from envault.env_scope import (
    ScopeError,
    assign_scope,
    get_scopes,
    keys_in_scope,
    list_scopes,
    remove_scope,
)


def _vp(ctx: click.Context) -> str:
    return ctx.obj["vault_path"]


@click.group("scope")
def scope_group() -> None:
    """Manage key scopes (dev / staging / prod …)."""


@scope_group.command("assign")
@click.argument("key")
@click.argument("scope")
@click.pass_context
def scope_assign(ctx: click.Context, key: str, scope: str) -> None:
    """Assign KEY to SCOPE."""
    try:
        scopes = assign_scope(_vp(ctx), key, scope)
        click.echo(f"Assigned '{key}' to scope '{scope}'. Scopes: {', '.join(scopes)}")
    except ScopeError as exc:
        raise click.ClickException(str(exc)) from exc


@scope_group.command("remove")
@click.argument("key")
@click.argument("scope")
@click.pass_context
def scope_remove(ctx: click.Context, key: str, scope: str) -> None:
    """Remove SCOPE from KEY."""
    try:
        removed = remove_scope(_vp(ctx), key, scope)
        if removed:
            click.echo(f"Removed scope '{scope}' from '{key}'.")
        else:
            click.echo(f"Key '{key}' was not in scope '{scope}'.")
    except ScopeError as exc:
        raise click.ClickException(str(exc)) from exc


@scope_group.command("get")
@click.argument("key")
@click.pass_context
def scope_get(ctx: click.Context, key: str) -> None:
    """List all scopes assigned to KEY."""
    scopes = get_scopes(_vp(ctx), key)
    if scopes:
        click.echo(", ".join(scopes))
    else:
        click.echo(f"No scopes assigned to '{key}'.")


@scope_group.command("keys")
@click.argument("scope")
@click.pass_context
def scope_keys(ctx: click.Context, scope: str) -> None:
    """List all keys belonging to SCOPE."""
    keys = keys_in_scope(_vp(ctx), scope)
    if keys:
        for k in keys:
            click.echo(k)
    else:
        click.echo(f"No keys found in scope '{scope}'.")


@scope_group.command("list")
@click.pass_context
def scope_list(ctx: click.Context) -> None:
    """List all distinct scopes in the vault."""
    scopes = list_scopes(_vp(ctx))
    if scopes:
        for s in scopes:
            click.echo(s)
    else:
        click.echo("No scopes defined.")
