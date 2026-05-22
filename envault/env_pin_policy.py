"""Pin-based access policy: enforce PIN requirements before vault operations."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


class PinPolicyError(Exception):
    """Raised when a pin policy violation occurs."""


def _policy_path(vault_path: Path) -> Path:
    return vault_path.with_suffix(".pinpolicy.json")


def _load(vault_path: Path) -> dict:
    p = _policy_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(vault_path: Path, data: dict) -> None:
    _policy_path(vault_path).write_text(json.dumps(data, indent=2))


def set_policy(
    vault_path: Path,
    *,
    require_pin: bool = True,
    min_pin_length: int = 4,
    max_attempts: int = 3,
) -> dict:
    """Set the PIN policy for a vault."""
    if min_pin_length < 4:
        raise PinPolicyError("min_pin_length must be at least 4")
    if max_attempts < 1:
        raise PinPolicyError("max_attempts must be at least 1")
    policy = {
        "require_pin": require_pin,
        "min_pin_length": min_pin_length,
        "max_attempts": max_attempts,
    }
    _save(vault_path, policy)
    return policy


def get_policy(vault_path: Path) -> dict:
    """Return the current PIN policy (with defaults if not set)."""
    data = _load(vault_path)
    return {
        "require_pin": data.get("require_pin", False),
        "min_pin_length": data.get("min_pin_length", 4),
        "max_attempts": data.get("max_attempts", 3),
    }


def remove_policy(vault_path: Path) -> bool:
    """Remove the PIN policy file. Returns True if it existed."""
    p = _policy_path(vault_path)
    if p.exists():
        p.unlink()
        return True
    return False


def enforce_policy(vault_path: Path, pin: str) -> None:
    """Raise PinPolicyError if the PIN does not satisfy the policy."""
    policy = get_policy(vault_path)
    if not policy["require_pin"]:
        return
    if len(pin) < policy["min_pin_length"]:
        raise PinPolicyError(
            f"PIN must be at least {policy['min_pin_length']} characters"
        )
