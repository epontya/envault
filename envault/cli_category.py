"""CLI commands for key category management."""
import click

from envault.env_category import (
    CategoryError,
    assign_category,
    get_category,
    list_by_category,
    list_categories,
    remove_category,
)


def _vp(ctx: click.Context) -> str:
    return ctx.obj["vault_path"]


@click.group(name="category")
def category_group() -> None:
    """Manage categories for vault keys."""


@category_group.command("assign")
@click.argument("key")
@click.argument("category")
@click.pass_context
def category_assign(ctx: click.Context, key: str, category: str) -> None:
    """Assign CATEGORY to KEY."""
    try:
        result = assign_category(_vp(ctx), key, category)
        click.echo(f"Assigned '{result}' to '{key}'.")
    except CategoryError as exc:
        raise click.ClickException(str(exc))


@category_group.command("get")
@click.argument("key")
@click.pass_context
def category_get(ctx: click.Context, key: str) -> None:
    """Show the category assigned to KEY."""
    cat = get_category(_vp(ctx), key)
    if cat is None:
        raise click.ClickException(f"No category assigned to '{key}'.")
    click.echo(cat)


@category_group.command("remove")
@click.argument("key")
@click.pass_context
def category_remove(ctx: click.Context, key: str) -> None:
    """Remove category assignment from KEY."""
    removed = remove_category(_vp(ctx), key)
    if not removed:
        raise click.ClickException(f"No category assigned to '{key}'.")
    click.echo(f"Category removed from '{key}'.")


@category_group.command("list")
@click.option("--category", "-c", default=None, help="Filter by category name.")
@click.pass_context
def category_list(ctx: click.Context, category: str) -> None:
    """List categories or keys within a category."""
    vp = _vp(ctx)
    if category:
        keys = list_by_category(vp, category)
        if not keys:
            click.echo(f"No keys in category '{category}'.")
        else:
            for k in keys:
                click.echo(k)
    else:
        cats = list_categories(vp)
        if not cats:
            click.echo("No categories defined.")
        else:
            for c in cats:
                click.echo(c)
