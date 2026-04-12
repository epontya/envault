"""CLI commands for template rendering."""

from __future__ import annotations

import sys

import click

from envault.cli import get_vault
from envault.template import MissingKeyError, TemplateError, render_file, render_string


@click.group("template", help="Render templates using vault values.")
def template_group() -> None:  # pragma: no cover
    pass


@template_group.command("render")
@click.argument("template_file", type=click.Path(exists=True, dir_okay=False))
@click.option("--output", "-o", default="-", help="Output file path (default: stdout).")
@click.option("--vault", "vault_path", default=".envault", show_default=True)
@click.option("--password", prompt=True, hide_input=True, envvar="ENVAULT_PASSWORD")
@click.option(
    "--strict/--no-strict",
    default=True,
    show_default=True,
    help="Error on missing keys vs leave placeholder.",
)
def template_render(
    template_file: str,
    output: str,
    vault_path: str,
    password: str,
    strict: bool,
) -> None:
    """Render TEMPLATE_FILE substituting {{ KEY }} placeholders from the vault."""
    vault = get_vault(vault_path, password)
    try:
        result = render_file(template_file, vault, password, strict=strict)
    except MissingKeyError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
    except TemplateError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    if output == "-":
        click.echo(result, nl=False)
    else:
        with open(output, "w", encoding="utf-8") as fh:
            fh.write(result)
        click.echo(f"Rendered template written to '{output}'.")


@template_group.command("preview")
@click.argument("text")
@click.option("--vault", "vault_path", default=".envault", show_default=True)
@click.option("--password", prompt=True, hide_input=True, envvar="ENVAULT_PASSWORD")
@click.option("--strict/--no-strict", default=True, show_default=True)
def template_preview(
    text: str,
    vault_path: str,
    password: str,
    strict: bool,
) -> None:
    """Render an inline TEXT string and print the result."""
    vault = get_vault(vault_path, password)
    try:
        result = render_string(text, vault, password, strict=strict)
    except MissingKeyError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
    click.echo(result)
