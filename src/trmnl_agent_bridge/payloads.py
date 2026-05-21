"""Agent status payload loading, validation, and TRMNL wrapping."""

from __future__ import annotations

import json
import re
from typing import Any


DEFAULT_PAYLOAD_LIMIT_BYTES = 2048
STATE_VALUES = {"CLEAR", "WATCH", "ACTION", "BLOCKED", "FAIL"}
REQUIRED_FIELDS = ("schema_version", "source", "state", "headline", "detail", "updated")
OPTIONAL_FIELDS = ("title", "next", "signals", "health", "run_url", "repo", "branch", "task", "expires_at")
ALLOWED_FIELDS = set(REQUIRED_FIELDS) | set(OPTIONAL_FIELDS)


class PayloadError(RuntimeError):
    """Expected payload validation failure."""


def json_bytes(value: Any) -> bytes:
    return json.dumps(value, separators=(",", ":"), sort_keys=True).encode("utf-8")


def load_json_text(text: str) -> dict[str, Any]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise PayloadError(f"Payload is not valid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise PayloadError("Payload must be a JSON object.")
    return payload


def normalize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize an agent-status.v1 payload."""
    unknown = sorted(set(payload) - ALLOWED_FIELDS)
    if unknown:
        raise PayloadError(f"Unknown payload fields are not allowed: {', '.join(unknown)}")

    missing = [field for field in REQUIRED_FIELDS if field not in payload]
    if missing:
        raise PayloadError(f"Missing required payload fields: {', '.join(missing)}")

    schema_version = payload.get("schema_version")
    if schema_version != 1:
        raise PayloadError("schema_version must be 1.")

    state = str(payload.get("state", "")).strip().upper()
    if state not in STATE_VALUES:
        raise PayloadError(f"state must be one of: {', '.join(sorted(STATE_VALUES))}.")

    normalized: dict[str, Any] = {
        "schema_version": 1,
        "source": _required_short_string(payload, "source"),
        "state": state,
        "headline": _required_short_string(payload, "headline"),
        "detail": _required_short_string(payload, "detail"),
        "updated": _required_short_string(payload, "updated"),
    }

    title = _optional_short_string(payload, "title")
    normalized["title"] = title or "AGENT NOW"

    for field in ("next", "health", "run_url", "repo", "branch", "task", "expires_at"):
        value = _optional_short_string(payload, field)
        if value:
            normalized[field] = value

    signals = _normalize_signals(payload.get("signals", []))
    if signals:
        normalized["signals"] = signals

    return normalized


def merge_variables_body(
    payload: dict[str, Any],
    *,
    merge_strategy: str | None = None,
    stream_limit: int | None = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {"merge_variables": payload}
    if merge_strategy:
        body["merge_strategy"] = merge_strategy
    if stream_limit is not None:
        body["stream_limit"] = stream_limit
    return body


def payload_size_bytes(payload: dict[str, Any]) -> int:
    return len(json_bytes(payload))


def default_payload() -> dict[str, Any]:
    return normalize_payload(
        {
            "schema_version": 1,
            "source": "codex",
            "title": "AGENT NOW",
            "state": "ACTION",
            "headline": "Review failed test run",
            "detail": "One workflow needs attention.",
            "next": "Last run completed 14:12",
            "signals": ["Tests: 1 failed", "PR: ready", "Agent: idle"],
            "health": "TRMNL webhook OK | payload 612 bytes",
            "updated": "14:13",
        }
    )


def _required_short_string(payload: dict[str, Any], field: str) -> str:
    value = _optional_short_string(payload, field)
    if not value:
        raise PayloadError(f"{field} must be a non-empty string.")
    return value


def _optional_short_string(payload: dict[str, Any], field: str) -> str:
    value = payload.get(field)
    if value is None:
        return ""
    if not isinstance(value, str):
        raise PayloadError(f"{field} must be a string.")
    return re.sub(r"\s+", " ", value).strip()


def _normalize_signals(value: Any) -> list[str]:
    if value in (None, ""):
        return []
    if isinstance(value, dict):
        items = [f"{key}: {item}" for key, item in value.items()]
    elif isinstance(value, list):
        items = value
    else:
        raise PayloadError("signals must be an array of strings or a small object.")

    signals: list[str] = []
    for item in items:
        if not isinstance(item, str):
            raise PayloadError("signals must contain only strings after normalization.")
        signal = re.sub(r"\s+", " ", item).strip()
        if signal:
            signals.append(signal)
    return signals[:4]
