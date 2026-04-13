"""Webhook notifications for vault events."""
from __future__ import annotations

import json
import urllib.request
import urllib.error
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional


class WebhookError(Exception):
    """Raised when a webhook operation fails."""


@dataclass
class WebhookEntry:
    url: str
    events: List[str] = field(default_factory=list)  # empty = all events
    secret: Optional[str] = None


class WebhookStore:
    """Persist and fire webhook registrations for a vault."""

    def __init__(self, store_path: Path) -> None:
        self._path = store_path
        self._hooks: List[WebhookEntry] = self._load()

    def _load(self) -> List[WebhookEntry]:
        if not self._path.exists():
            return []
        raw = json.loads(self._path.read_text())
        return [WebhookEntry(**h) for h in raw]

    def _save(self) -> None:
        self._path.write_text(json.dumps([asdict(h) for h in self._hooks], indent=2))

    def add(self, url: str, events: Optional[List[str]] = None, secret: Optional[str] = None) -> WebhookEntry:
        if any(h.url == url for h in self._hooks):
            raise WebhookError(f"Webhook already registered: {url}")
        entry = WebhookEntry(url=url, events=events or [], secret=secret)
        self._hooks.append(entry)
        self._save()
        return entry

    def remove(self, url: str) -> bool:
        before = len(self._hooks)
        self._hooks = [h for h in self._hooks if h.url != url]
        if len(self._hooks) < before:
            self._save()
            return True
        return False

    def list(self) -> List[WebhookEntry]:
        return list(self._hooks)

    def fire(self, event: str, payload: dict) -> List[str]:
        """Send event to matching hooks. Returns list of URLs that failed."""
        failed: List[str] = []
        body = json.dumps({"event": event, "payload": payload}).encode()
        for hook in self._hooks:
            if hook.events and event not in hook.events:
                continue
            headers = {"Content-Type": "application/json"}
            if hook.secret:
                headers["X-Envault-Secret"] = hook.secret
            req = urllib.request.Request(hook.url, data=body, headers=headers, method="POST")
            try:
                with urllib.request.urlopen(req, timeout=5):
                    pass
            except (urllib.error.URLError, OSError):
                failed.append(hook.url)
        return failed
