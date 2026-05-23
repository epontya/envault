"""CLI commands for key priority management."""
import click

from envault.env_priority import (
    PRIORITY_LEVELS,
    PriorityError,
    get_priority,
    list_by_priority,
    remove_priority,
    set_priority,
)


def _vp(ctx: click.Context) -> str:
    return ctx.obj["vault_file"]


@click.group("priority")
def priority_group() -> None:
    """Manage key priority levels."""


@priority_group.command("set")
@click.argument("key")
@click.argument("level", type=click.Choice(PRIORITY_LEVELS, case_sensitive=False))
@click.pass_context
def priority_set(ctx: click.Context, key: str, level: str) -> None:
    """Assign LEVEL to KEY."""
    try:
        result = set_priority(_vp(ctx), key, level.lower())
        click.echo(f"Priority for '{key}' set to '{result}'.")
    except PriorityError as exc:
        raise click.ClickException(str(exc)) from exc


@priority_group.command("get")
@click.argument("key")
@click.pass_context
def priority_get(ctx: click.Context, key: str) -> None:
    """Show the priority level for KEY."""
    level = get_priority(_vp(ctx), key)
    if level is None:
        raise click.ClickException(f"No priority set for '{key}'.")
    click.echo(level)


@priority_group.command("remove")
@click.argument("key")
@click.pass_context
def priority_remove(ctx: click.Context, key: str) -> None:
    """Remove the priority assignment for KEY."""
    removed = remove_priority(_vp(ctx), key)
    if removed:
        click.echo(f"Priority for '{key}' removed.")
    else:
        raise click.ClickException(f"No priority set for '{key}'.")


@priority_group.command("list")
@click.option("--level", type=click.Choice(PRIORITY_LEVELS, case_sensitive=False), default=None)
@click.pass_context
def priority_list(ctx: click.Context, level: str | None) -> None:
    """List all priority assignments, optionally filtered by LEVEL."""
    try:
        data = list_by_priority(_vp(ctx), level)
    except PriorityError as exc:
        raise click.ClickException(str(exc)) from exc
    if not data:
        click.echo("No priority assignments found.")
        return
    for key, lvl in sorted(data.items()):
        click.echo(f"{key}: {lvl}")
