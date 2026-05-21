"""Credential lookup helpers for TRMNL agent bridge."""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass


KEYCHAIN_SERVICE = "TRMNL Agent Bridge"
KEYCHAIN_ACCOUNTS = ("TRMNL_WEBHOOK_URL", "TRMNL_ACCESS_TOKEN", "TRMNL_DEVICE_ID")


class CredentialError(RuntimeError):
    """Expected credential storage failure."""


@dataclass(frozen=True)
class Credential:
    name: str
    value: str | None
    source: str


def keychain_lookup(account: str, service: str = KEYCHAIN_SERVICE) -> str | None:
    """Return a macOS Keychain value when available."""
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-s", service, "-a", account, "-w"],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception:
        return None
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return value or None


def keychain_store(account: str, value: str, service: str = KEYCHAIN_SERVICE) -> None:
    """Store one supported credential in macOS Keychain."""
    if account not in KEYCHAIN_ACCOUNTS:
        raise CredentialError(f"Unsupported Keychain account {account!r}.")
    result = subprocess.run(
        ["security", "add-generic-password", "-U", "-s", service, "-a", account, "-w", value],
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise CredentialError(f"Could not store {account} in Keychain: {detail}")


def resolve_credential(
    explicit_value: str | None,
    env_name: str,
    *,
    use_keychain: bool = True,
) -> Credential:
    """Resolve a credential from argument, environment, then Keychain."""
    if explicit_value:
        return Credential(name=env_name, value=explicit_value, source="argument")
    env_value = os.environ.get(env_name)
    if env_value:
        return Credential(name=env_name, value=env_value, source="environment")
    if use_keychain:
        keychain_value = keychain_lookup(env_name)
        if keychain_value:
            return Credential(name=env_name, value=keychain_value, source="keychain")
    return Credential(name=env_name, value=None, source="missing")


def redact_secret(value: str | None) -> str:
    """Return a stable redacted representation without leaking the full value."""
    if not value:
        return "<missing>"
    return "<set>"
