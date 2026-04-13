"""Tests for envault.webhook and envault.cli_webhook."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from envault.webhook import WebhookStore, WebhookError
from envault.cli_webhook import webhook_group


@pytest.fixture()
def store(tmp_path: Path) -> WebhookStore:
    return WebhookStore(tmp_path / "vault.webhooks.json")


# --- unit tests ---

def test_add_creates_file(store: WebhookStore, tmp_path: Path) -> None:
    store.add("https://example.com/hook")
    assert (tmp_path / "vault.webhooks.json").exists()


def test_add_and_list(store: WebhookStore) -> None:
    store.add("https://a.example.com", events=["set", "delete"])
    hooks = store.list()
    assert len(hooks) == 1
    assert hooks[0].url == "https://a.example.com"
    assert hooks[0].events == ["set", "delete"]


def test_duplicate_url_raises(store: WebhookStore) -> None:
    store.add("https://dup.example.com")
    with pytest.raises(WebhookError, match="already registered"):
        store.add("https://dup.example.com")


def test_remove_existing(store: WebhookStore) -> None:
    store.add("https://rm.example.com")
    assert store.remove("https://rm.example.com") is True
    assert store.list() == []


def test_remove_missing_returns_false(store: WebhookStore) -> None:
    assert store.remove("https://ghost.example.com") is False


def test_fire_posts_to_matching_hooks(store: WebhookStore) -> None:
    store.add("https://hook.example.com", events=["set"])
    mock_resp = MagicMock()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
        failed = store.fire("set", {"key": "FOO"})
    assert failed == []
    mock_open.assert_called_once()


def test_fire_skips_non_matching_event(store: WebhookStore) -> None:
    store.add("https://hook.example.com", events=["delete"])
    with patch("urllib.request.urlopen") as mock_open:
        failed = store.fire("set", {"key": "FOO"})
    mock_open.assert_not_called()
    assert failed == []


def test_fire_returns_failed_on_error(store: WebhookStore) -> None:
    import urllib.error
    store.add("https://bad.example.com")
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("timeout")):
        failed = store.fire("set", {})
    assert "https://bad.example.com" in failed


# --- CLI tests ---

@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def vault_file(tmp_path: Path) -> str:
    return str(tmp_path / "test.vault")


def _invoke(runner: CliRunner, vault_file: str, *args: str):
    return runner.invoke(webhook_group, ["--vault", vault_file, *args])


def test_cli_add_webhook(runner: CliRunner, vault_file: str) -> None:
    result = runner.invoke(webhook_group, ["add", "https://x.example.com", "--vault", vault_file])
    assert result.exit_code == 0
    assert "Registered" in result.output


def test_cli_list_empty(runner: CliRunner, vault_file: str) -> None:
    result = runner.invoke(webhook_group, ["list", "--vault", vault_file])
    assert result.exit_code == 0
    assert "No webhooks" in result.output


def test_cli_remove_nonexistent_exits_nonzero(runner: CliRunner, vault_file: str) -> None:
    result = runner.invoke(webhook_group, ["remove", "https://none.example.com", "--vault", vault_file])
    assert result.exit_code != 0
