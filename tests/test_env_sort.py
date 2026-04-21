"""Tests for envault.env_sort."""
import pytest

from envault.env_sort import (
    SortBy,
    SortError,
    SortOrder,
    sort_entries,
    sorted_keys,
)


@pytest.fixture()
def sample() -> dict:
    return {
        "ZEBRA": "alpha",
        "apple": "Mango",
        "Banana": "  kiwi  ",
        "mango": "bb",
    }


def test_sort_by_key_asc_case_insensitive(sample):
    result = sort_entries(sample, by=SortBy.KEY, order=SortOrder.ASC)
    keys = [k for k, _ in result]
    assert keys == sorted(sample.keys(), key=str.lower)


def test_sort_by_key_desc(sample):
    result = sort_entries(sample, by=SortBy.KEY, order=SortOrder.DESC)
    keys = [k for k, _ in result]
    assert keys == sorted(sample.keys(), key=str.lower, reverse=True)


def test_sort_by_key_case_sensitive(sample):
    result = sort_entries(sample, by=SortBy.KEY, order=SortOrder.ASC, case_sensitive=True)
    keys = [k for k, _ in result]
    assert keys == sorted(sample.keys())


def test_sort_by_value_asc(sample):
    result = sort_entries(sample, by=SortBy.VALUE, order=SortOrder.ASC)
    values = [v for _, v in result]
    assert values == sorted(sample.values(), key=str.lower)


def test_sort_by_value_desc(sample):
    result = sort_entries(sample, by=SortBy.VALUE, order=SortOrder.DESC)
    values = [v for _, v in result]
    assert values == sorted(sample.values(), key=str.lower, reverse=True)


def test_sort_by_length_asc(sample):
    result = sort_entries(sample, by=SortBy.LENGTH, order=SortOrder.ASC)
    lengths = [len(v) for _, v in result]
    assert lengths == sorted(lengths)


def test_sort_by_length_desc(sample):
    result = sort_entries(sample, by=SortBy.LENGTH, order=SortOrder.DESC)
    lengths = [len(v) for _, v in result]
    assert lengths == sorted(lengths, reverse=True)


def test_sort_empty_dict():
    assert sort_entries({}) == []


def test_sort_single_entry():
    result = sort_entries({"ONLY": "val"})
    assert result == [("ONLY", "val")]


def test_sorted_keys_returns_keys_only(sample):
    keys = sorted_keys(sample)
    assert all(isinstance(k, str) for k in keys)
    assert set(keys) == set(sample.keys())


def test_sorted_keys_asc_order(sample):
    keys = sorted_keys(sample, order=SortOrder.ASC)
    assert keys == sorted(sample.keys(), key=str.lower)


def test_sorted_keys_desc_order(sample):
    keys = sorted_keys(sample, order=SortOrder.DESC)
    assert keys == sorted(sample.keys(), key=str.lower, reverse=True)


def test_invalid_sort_by_raises():
    with pytest.raises((SortError, ValueError)):
        sort_entries({"K": "v"}, by="nonexistent")  # type: ignore[arg-type]
