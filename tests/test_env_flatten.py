"""Tests for envault.env_flatten."""

import pytest

from envault.env_flatten import FlattenError, flatten, unflatten


# ---------------------------------------------------------------------------
# flatten()
# ---------------------------------------------------------------------------


def test_flatten_simple_dict():
    result = flatten({"db": {"host": "localhost", "port": "5432"}})
    assert result == {"DB_HOST": "localhost", "DB_PORT": "5432"}


def test_flatten_three_levels_deep():
    data = {"aws": {"s3": {"bucket": "my-bucket"}}}
    result = flatten(data)
    assert result == {"AWS_S3_BUCKET": "my-bucket"}


def test_flatten_lowercase_keys_when_uppercase_false():
    result = flatten({"db": {"host": "localhost"}}, uppercase_keys=False)
    assert "db_host" in result
    assert "DB_HOST" not in result


def test_flatten_custom_separator():
    result = flatten({"db": {"host": "localhost"}}, separator=".", uppercase_keys=False)
    assert result == {"db.host": "localhost"}


def test_flatten_scalar_values_converted_to_str():
    result = flatten({"port": 5432, "debug": True, "ratio": 0.5})
    assert result["PORT"] == "5432"
    assert result["DEBUG"] == "True"
    assert result["RATIO"] == "0.5"


def test_flatten_none_value_becomes_empty_string():
    result = flatten({"key": None})
    assert result["KEY"] == ""


def test_flatten_already_flat_dict():
    result = flatten({"FOO": "bar", "BAZ": "qux"}, uppercase_keys=False)
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_flatten_empty_dict_returns_empty():
    assert flatten({}) == {}


def test_flatten_non_dict_raises():
    with pytest.raises(FlattenError, match="Top-level input must be a dict"):
        flatten(["not", "a", "dict"])  # type: ignore[arg-type]


def test_flatten_empty_separator_raises():
    with pytest.raises(FlattenError, match="Separator"):
        flatten({"a": "b"}, separator="")


def test_flatten_unsupported_value_type_raises():
    with pytest.raises(FlattenError, match="Unsupported value type"):
        flatten({"key": ["list", "value"]})


def test_flatten_empty_key_raises():
    with pytest.raises(FlattenError, match="Invalid key"):
        flatten({"": "value"})


# ---------------------------------------------------------------------------
# unflatten()
# ---------------------------------------------------------------------------


def test_unflatten_simple():
    result = unflatten({"DB_HOST": "localhost", "DB_PORT": "5432"})
    assert result == {"DB": {"HOST": "localhost", "PORT": "5432"}}


def test_unflatten_no_separator_key_stays_flat():
    result = unflatten({"SIMPLE": "value"})
    assert result == {"SIMPLE": "value"}


def test_unflatten_empty_dict_returns_empty():
    assert unflatten({}) == {}


def test_unflatten_empty_separator_raises():
    with pytest.raises(FlattenError, match="Separator"):
        unflatten({"A_B": "v"}, separator="")


def test_unflatten_key_collision_raises():
    # "FOO" appears as both a plain key and a branch prefix
    with pytest.raises(FlattenError, match="collision"):
        unflatten({"FOO": "plain", "FOO_BAR": "nested"})


def test_flatten_then_unflatten_round_trip():
    original = {"db": {"host": "localhost", "port": "5432"}}
    flat = flatten(original, uppercase_keys=False)
    recovered = unflatten(flat)
    assert recovered == {"db": {"host": "localhost", "port": "5432"}}
