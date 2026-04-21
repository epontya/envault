"""Tests for envault.env_transform."""
from __future__ import annotations

import pytest

from envault.env_transform import (
    TransformError,
    apply_transform,
    apply_transforms,
    list_transforms,
    transform_dict,
)


# ---------------------------------------------------------------------------
# list_transforms
# ---------------------------------------------------------------------------

def test_list_transforms_returns_known_names():
    names = list_transforms()
    assert "upper" in names
    assert "lower" in names
    assert "strip" in names
    assert "trim_quotes" in names
    assert "mask" in names


def test_list_transforms_is_sorted():
    names = list_transforms()
    assert names == sorted(names)


# ---------------------------------------------------------------------------
# apply_transform
# ---------------------------------------------------------------------------

def test_upper():
    assert apply_transform("upper", "hello") == "HELLO"


def test_lower():
    assert apply_transform("lower", "WORLD") == "world"


def test_strip():
    assert apply_transform("strip", "  hi  ") == "hi"


def test_trim_quotes_double():
    assert apply_transform("trim_quotes", '"secret"') == "secret"


def test_trim_quotes_single():
    assert apply_transform("trim_quotes", "'value'") == "value"


def test_trim_quotes_no_quotes_unchanged():
    assert apply_transform("trim_quotes", "plain") == "plain"


def test_mask_long_value():
    result = apply_transform("mask", "mysecret")
    assert result.endswith("et")
    assert result.startswith("*")
    assert len(result) == len("mysecret")


def test_mask_short_value():
    assert apply_transform("mask", "ab") == "**"


def test_unknown_transform_raises():
    with pytest.raises(TransformError, match="Unknown transform"):
        apply_transform("nonexistent", "value")


# ---------------------------------------------------------------------------
# apply_transforms (pipeline)
# ---------------------------------------------------------------------------

def test_pipeline_strip_then_upper():
    assert apply_transforms(["strip", "upper"], "  hello  ") == "HELLO"


def test_pipeline_empty_returns_unchanged():
    assert apply_transforms([], "unchanged") == "unchanged"


def test_pipeline_raises_on_bad_transform():
    with pytest.raises(TransformError):
        apply_transforms(["upper", "bogus"], "value")


# ---------------------------------------------------------------------------
# transform_dict
# ---------------------------------------------------------------------------

def test_transform_dict_all_keys():
    data = {"A": "hello", "B": "world"}
    result = transform_dict(data, ["upper"])
    assert result == {"A": "HELLO", "B": "WORLD"}


def test_transform_dict_with_pattern():
    data = {"DB_HOST": "localhost", "APP_NAME": "envault", "DB_PORT": "5432"}
    result = transform_dict(data, ["upper"], key_pattern="DB_*")
    assert result["DB_HOST"] == "LOCALHOST"
    assert result["DB_PORT"] == "5432"  # already upper, unchanged either way
    assert result["APP_NAME"] == "envault"  # not matched, untouched


def test_transform_dict_no_match_returns_original():
    data = {"X": "value"}
    result = transform_dict(data, ["upper"], key_pattern="NOMATCH_*")
    assert result == {"X": "value"}


def test_transform_dict_does_not_mutate_input():
    data = {"K": "  spaced  "}
    transform_dict(data, ["strip"])
    assert data["K"] == "  spaced  "
