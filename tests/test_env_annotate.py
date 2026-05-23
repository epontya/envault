"""Tests for envault.env_annotate."""
from __future__ import annotations

import pytest

from envault.env_annotate import (
    AnnotateError,
    get_annotation,
    list_annotations,
    remove_annotation,
    set_annotation,
)


@pytest.fixture()
def vpath(tmp_path):
    return tmp_path / "test.vault"


def test_set_annotation_creates_file(vpath):
    ap = vpath.parent / (vpath.stem + ".annotations.json")
    assert not ap.exists()
    set_annotation(vpath, "MY_KEY", "owner", "alice")
    assert ap.exists()


def test_set_annotation_returns_entry(vpath):
    result = set_annotation(vpath, "MY_KEY", "owner", "alice")
    assert result == {"owner": "alice"}


def test_set_multiple_fields_same_key(vpath):
    set_annotation(vpath, "DB_URL", "owner", "bob")
    set_annotation(vpath, "DB_URL", "env", "production")
    result = get_annotation(vpath, "DB_URL")
    assert result == {"owner": "bob", "env": "production"}


def test_set_annotation_empty_key_raises(vpath):
    with pytest.raises(AnnotateError, match="key"):
        set_annotation(vpath, "", "field", "value")


def test_set_annotation_empty_field_raises(vpath):
    with pytest.raises(AnnotateError, match="field"):
        set_annotation(vpath, "KEY", "", "value")


def test_get_annotation_specific_field(vpath):
    set_annotation(vpath, "API_KEY", "tier", "gold")
    assert get_annotation(vpath, "API_KEY", "tier") == "gold"


def test_get_annotation_missing_field_returns_none(vpath):
    set_annotation(vpath, "API_KEY", "tier", "gold")
    assert get_annotation(vpath, "API_KEY", "nonexistent") is None


def test_get_annotation_missing_key_returns_empty_dict(vpath):
    result = get_annotation(vpath, "GHOST_KEY")
    assert result == {}


def test_remove_annotation_returns_true_when_existed(vpath):
    set_annotation(vpath, "SECRET", "note", "rotate soon")
    assert remove_annotation(vpath, "SECRET", "note") is True


def test_remove_annotation_cleans_up_empty_key(vpath):
    set_annotation(vpath, "SECRET", "note", "rotate soon")
    remove_annotation(vpath, "SECRET", "note")
    assert get_annotation(vpath, "SECRET") == {}


def test_remove_annotation_missing_field_returns_false(vpath):
    assert remove_annotation(vpath, "KEY", "no_such_field") is False


def test_list_annotations_empty_when_no_file(vpath):
    assert list_annotations(vpath) == {}


def test_list_annotations_returns_all(vpath):
    set_annotation(vpath, "A", "owner", "alice")
    set_annotation(vpath, "B", "env", "staging")
    result = list_annotations(vpath)
    assert "A" in result
    assert "B" in result
    assert result["A"]["owner"] == "alice"


def test_overwrite_annotation_field(vpath):
    set_annotation(vpath, "KEY", "owner", "alice")
    set_annotation(vpath, "KEY", "owner", "bob")
    assert get_annotation(vpath, "KEY", "owner") == "bob"
