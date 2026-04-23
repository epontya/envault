"""Tests for envault.env_diff_report."""
from __future__ import annotations

import pytest

from envault.env_diff_report import build_report, DiffReport, DiffReportEntry


# ---------------------------------------------------------------------------
# build_report
# ---------------------------------------------------------------------------

def test_added_key():
    report = build_report({}, {"KEY": "val"})
    assert len(report.added) == 1
    assert report.added[0].key == "KEY"
    assert report.added[0].new_value == "val"


def test_removed_key():
    report = build_report({"KEY": "val"}, {})
    assert len(report.removed) == 1
    assert report.removed[0].key == "KEY"
    assert report.removed[0].old_value == "val"


def test_changed_key():
    report = build_report({"KEY": "old"}, {"KEY": "new"})
    assert len(report.changed) == 1
    e = report.changed[0]
    assert e.old_value == "old"
    assert e.new_value == "new"


def test_unchanged_key_excluded_by_default():
    report = build_report({"KEY": "same"}, {"KEY": "same"})
    assert report.unchanged == []
    assert not report.has_differences()


def test_unchanged_key_included_when_requested():
    report = build_report({"KEY": "same"}, {"KEY": "same"}, include_unchanged=True)
    assert len(report.unchanged) == 1


def test_mixed_diff():
    old = {"A": "1", "B": "2", "C": "3"}
    new = {"A": "1", "B": "changed", "D": "4"}
    report = build_report(old, new)
    assert len(report.added) == 1    # D
    assert len(report.removed) == 1  # C
    assert len(report.changed) == 1  # B
    assert report.has_differences()


def test_empty_dicts_no_differences():
    report = build_report({}, {})
    assert not report.has_differences()


# ---------------------------------------------------------------------------
# summary
# ---------------------------------------------------------------------------

def test_summary_no_differences():
    report = build_report({"K": "v"}, {"K": "v"})
    assert report.summary() == "No differences found."


def test_summary_contains_counts():
    report = build_report({"A": "1"}, {"B": "2"})
    s = report.summary()
    assert "+1 added" in s
    assert "-1 removed" in s


def test_summary_changed():
    report = build_report({"A": "old"}, {"A": "new"})
    assert "~1 changed" in report.summary()


# ---------------------------------------------------------------------------
# to_text
# ---------------------------------------------------------------------------

def test_to_text_added_prefix():
    report = build_report({}, {"NEW_KEY": "v"})
    assert "+ NEW_KEY" in report.to_text()


def test_to_text_removed_prefix():
    report = build_report({"OLD_KEY": "v"}, {})
    assert "- OLD_KEY" in report.to_text()


def test_to_text_changed_prefix():
    report = build_report({"K": "old"}, {"K": "new"})
    assert "~ K" in report.to_text()


def test_to_text_no_diff_message():
    report = build_report({}, {})
    assert "no differences" in report.to_text()


def test_to_text_show_values_not_redacted():
    report = build_report({}, {"KEY": "secret"})
    text = report.to_text(show_values=True, redact=False)
    assert "secret" in text


def test_to_text_redact_hides_values():
    report = build_report({}, {"KEY": "secret"})
    text = report.to_text(show_values=True, redact=True)
    assert "secret" not in text


# ---------------------------------------------------------------------------
# DiffReportEntry.to_dict
# ---------------------------------------------------------------------------

def test_entry_to_dict_keys():
    e = DiffReportEntry(key="K", status="added", new_value="v")
    d = e.to_dict()
    assert set(d.keys()) == {"key", "status", "old_value", "new_value"}
    assert d["key"] == "K"
    assert d["status"] == "added"
    assert d["new_value"] == "v"
    assert d["old_value"] is None
