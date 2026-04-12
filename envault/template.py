"""Template rendering: substitute vault values into template strings."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from envault.vault import Vault

_PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")


class TemplateError(Exception):
    """Raised when template rendering fails."""


class MissingKeyError(TemplateError):
    """Raised when a placeholder key is not found in the vault."""

    def __init__(self, key: str) -> None:
        self.key = key
        super().__init__(f"Template placeholder '{{{{ {key} }}}}' not found in vault")


def render_string(template: str, vault: "Vault", password: str, strict: bool = True) -> str:
    """Replace ``{{ KEY }}`` placeholders with values from *vault*.

    Parameters
    ----------
    template:
        Raw template text containing ``{{ KEY }}`` placeholders.
    vault:
        Open :class:`~envault.vault.Vault` instance to read values from.
    password:
        Password used to decrypt vault entries.
    strict:
        When *True* (default) raise :class:`MissingKeyError` for unknown keys;
        when *False* leave the placeholder unchanged.
    """

    def _replace(match: re.Match) -> str:  # type: ignore[type-arg]
        key = match.group(1)
        value = vault.get(key, password)
        if value is None:
            if strict:
                raise MissingKeyError(key)
            return match.group(0)
        return value

    return _PLACEHOLDER_RE.sub(_replace, template)


def render_file(src_path: str, vault: "Vault", password: str, strict: bool = True) -> str:
    """Read *src_path* and render it with :func:`render_string`."""
    try:
        with open(src_path, "r", encoding="utf-8") as fh:
            content = fh.read()
    except OSError as exc:
        raise TemplateError(f"Cannot read template file '{src_path}': {exc}") from exc
    return render_string(content, vault, password, strict=strict)
