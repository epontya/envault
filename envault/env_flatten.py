"""Flatten nested dict structures into dot-notation environment variable keys."""

from __future__ import annotations

from typing import Any


class FlattenError(Exception):
    """Raised when flattening fails."""


def _flatten_dict(
    data: dict[str, Any],
    parent_key: str = "",
    separator: str = "_",
) -> dict[str, str]:
    """Recursively flatten a nested dict into a flat dict with compound keys."""
    items: dict[str, str] = {}
    for k, v in data.items():
        if not isinstance(k, str) or not k:
            raise FlattenError(f"Invalid key: {k!r}. All keys must be non-empty strings.")
        new_key = f"{parent_key}{separator}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(_flatten_dict(v, new_key, separator))
        elif isinstance(v, (str, int, float, bool)) or v is None:
            items[new_key] = "" if v is None else str(v)
        else:
            raise FlattenError(
                f"Unsupported value type {type(v).__name__!r} at key {new_key!r}."
            )
    return items


def flatten(
    data: dict[str, Any],
    separator: str = "_",
    uppercase_keys: bool = True,
) -> dict[str, str]:
    """Flatten *data* into a single-level dict suitable for env var storage.

    Parameters
    ----------
    data:
        Arbitrarily nested mapping whose leaf values are scalars.
    separator:
        String used to join key segments (default ``"_"``).
    uppercase_keys:
        When *True* (default) all resulting keys are uppercased.

    Returns
    -------
    dict[str, str]
        Flat mapping of string keys to string values.
    """
    if not isinstance(data, dict):
        raise FlattenError("Top-level input must be a dict.")
    if not separator:
        raise FlattenError("Separator must be a non-empty string.")

    flat = _flatten_dict(data, separator=separator)
    if uppercase_keys:
        flat = {k.upper(): v for k, v in flat.items()}
    return flat


def unflatten(
    data: dict[str, str],
    separator: str = "_",
) -> dict[str, Any]:
    """Reconstruct a nested dict from a flat dot/separator-notation mapping.

    Only the *first* separator occurrence is used to split each key, so
    ``FOO_BAR_BAZ`` with separator ``"_"`` becomes ``{"FOO": {"BAR_BAZ": ...}}``
    when called once — callers should apply iteratively or use a unique separator
    to achieve full nesting.

    For simple two-level nesting this is the inverse of :func:`flatten`.
    """
    if not separator:
        raise FlattenError("Separator must be a non-empty string.")

    result: dict[str, Any] = {}
    for key, value in data.items():
        if separator in key:
            parent, child = key.split(separator, 1)
            if parent not in result:
                result[parent] = {}
            if not isinstance(result[parent], dict):
                raise FlattenError(
                    f"Key collision: {parent!r} is both a leaf and a branch."
                )
            result[parent][child] = value
        else:
            if key in result and isinstance(result[key], dict):
                raise FlattenError(
                    f"Key collision: {key!r} is both a leaf and a branch."
                )
            result[key] = value
    return result
