"""CLI commands for managing key comments/annotations."""
from __future__ import annotations

import click

from envault.env_comment import (
    CommentError,
    get_comment,
    list_comments,
    remove_comment,
    set_comment,
)


@click.group("comment", help="Attach comments/annotations to vault keys.")
def comment_group() -> None:  # pragma: no cover
    pass


@comment_group.command("set")
@click.option("--vault", required=True, help="Path to the vault file.")
@click.argument("key")
@click.argument("comment")
def comment_set(vault: str, key: str, comment: str) -> None:
    """Attach COMMENT to KEY."""
    try:
        set_comment(vault, key, comment)
        click.echo(f"Comment set for '{key}'.")
    except CommentError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@comment_group.command("get")
@click.option("--vault", required=True, help="Path to the vault file.")
@click.argument("key")
def comment_get(vault: str, key: str) -> None:
    """Show the comment attached to KEY."""
    value = get_comment(vault, key)
    if value is None:
        click.echo(f"No comment set for '{key}'.", err=True)
        raise SystemExit(1)
    click.echo(value)


@comment_group.command("remove")
@click.option("--vault", required=True, help="Path to the vault file.")
@click.argument("key")
def comment_remove(vault: str, key: str) -> None:
    """Remove the comment attached to KEY."""
    try:
        existed = remove_comment(vault, key)
    except CommentError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    if existed:
        click.echo(f"Comment removed for '{key}'.")
    else:
        click.echo(f"No comment found for '{key}'.", err=True)
        raise SystemExit(1)


@comment_group.command("list")
@click.option("--vault", required=True, help="Path to the vault file.")
def comment_list(vault: str) -> None:
    """List all key comments for the vault."""
    try:
        entries = list_comments(vault)
    except CommentError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    if not entries:
        click.echo("No comments defined.")
        return
    for key, comment in sorted(entries.items()):
        click.echo(f"{key}: {comment}")
