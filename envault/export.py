"""Export vault secrets to various shell-compatible formats."""

from __future__ import annotations

from typing import Dict


SUPPORTED_FORMATS = ("dotenv", "shell", "json")


def export_dotenv(secrets: Dict[str, str]) -> str:
    """Return secrets formatted as a .env file.

    Each line is KEY=VALUE.  Values containing whitespace or special
    characters are double-quoted and internal double-quotes are escaped.
    """
    lines: list[str] = []
    for key, value in sorted(secrets.items()):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        if any(c in value for c in (" ", "\t", "\n", "#", "$", "'", '"', "=")):
            lines.append(f'{key}="{escaped}"')
        else:
            lines.append(f"{key}={value}")
    return "\n".join(lines) + ("\n" if lines else "")


def export_shell(secrets: Dict[str, str]) -> str:
    """Return secrets as POSIX export statements.

    Suitable for sourcing directly in bash/zsh: ``source <(envault export)``
    """
    lines: list[str] = []
    for key, value in sorted(secrets.items()):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'export {key}="{escaped}"')
    return "\n".join(lines) + ("\n" if lines else "")


def export_json(secrets: Dict[str, str]) -> str:
    """Return secrets serialised as a JSON object (pretty-printed)."""
    import json

    return json.dumps(secrets, indent=2, sort_keys=True) + "\n"


def export_secrets(secrets: Dict[str, str], fmt: str = "dotenv") -> str:
    """Dispatch to the correct formatter.

    Parameters
    ----------
    secrets:
        Mapping of variable name -> plaintext value.
    fmt:
        One of ``'dotenv'``, ``'shell'``, or ``'json'``.

    Raises
    ------
    ValueError
        If *fmt* is not a recognised format.
    """
    if fmt == "dotenv":
        return export_dotenv(secrets)
    if fmt == "shell":
        return export_shell(secrets)
    if fmt == "json":
        return export_json(secrets)
    raise ValueError(
        f"Unknown format {fmt!r}. Choose one of: {', '.join(SUPPORTED_FORMATS)}"
    )
