"""CLI commands for managing key annotations."""
from __future__ import annotations

import click

from envault.env_annotate import (
    AnnotateError,
    get_annotation,
    list_annotations,
    remove_annotation,
    set_annotation,
)


def _vp(ctx: click.Context) -> str:
    return ctx.obj["vault_path"]


@click.group("annotate")
def annotate_group() -> None:
    """Attach metadata annotations to vault keys."""


@annotate_group.command("set")
@click.argument("key")
@click.argument("field")
@click.argument("value")
@click.pass_context
def annotate_set(ctx: click.Context, key: str, field: str, value: str) -> None:
    """Set annotation FIELD=VALUE on KEY."""
    try:
        result = set_annotation(_vp(ctx), key, field, value)
        click.echo(f"Annotation set: {key}[{field}] = {result[field]}")
    except AnnotateError as exc:
        raise click.ClickException(str(exc)) from exc


@annotate_group.command("get")
@click.argument("key")
@click.argument("field", required=False, default=None)
@click.pass_context
def annotate_get(ctx: click.Context, key: str, field: str | None) -> None:
    """Get annotation(s) for KEY, optionally scoped to FIELD."""
    result = get_annotation(_vp(ctx), key, field)
    if result is None:
        raise click.ClickException(f"No annotation '{field}' found for key '{key}'.")
    if isinstance(result, dict):
        if not result:
            click.echo(f"No annotations for '{key}'.")
        else:
            for f, v in sorted(result.items()):
                click.echo(f"  {f}: {v}")
    else:
        click.echo(str(result))


@annotate_group.command("remove")
@click.argument("key")
@click.argument("field")
@click.pass_context
def annotate_remove(ctx: click.Context, key: str, field: str) -> None:
    """Remove annotation FIELD from KEY."""
    removed = remove_annotation(_vp(ctx), key, field)
    if removed:
        click.echo(f"Removed annotation '{field}' from '{key}'.")
    else:
        raise click.ClickException(f"Annotation '{field}' not found on key '{key}'.")


@annotate_group.command("list")
@click.pass_context
def annotate_list(ctx: click.Context) -> None:
    """List all annotations across all keys."""
    all_ann = list_annotations(_vp(ctx))
    if not all_ann:
        click.echo("No annotations stored.")
        return
    for key, fields in sorted(all_ann.items()):
        for field, value in sorted(fields.items()):
            click.echo(f"{key}  {field}: {value}")
