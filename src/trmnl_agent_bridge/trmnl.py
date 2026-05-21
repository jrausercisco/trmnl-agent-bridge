"""TRMNL API helpers."""

from __future__ import annotations

import hashlib
import json
import pathlib
import urllib.error
import urllib.request
from typing import Any

from .payloads import json_bytes


TRMNL_BASE_URL = "https://trmnl.com"
USER_AGENT = "trmnl-agent-bridge/0.1.2"


class TrmnlError(RuntimeError):
    """Expected TRMNL request failure."""


def request_json(
    url: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    payload: Any | None = None,
    timeout: int = 30,
) -> tuple[int, dict[str, str], Any, bytes]:
    data = json_bytes(payload) if payload is not None else None
    req_headers = {"User-Agent": USER_AGENT}
    if headers:
        req_headers.update(headers)
    if data is not None:
        req_headers.setdefault("Content-Type", "application/json")
    request = urllib.request.Request(url, data=data, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read()
            return response.status, dict(response.headers), _decode_body(body), body
    except urllib.error.HTTPError as exc:
        body = exc.read()
        decoded = _decode_body(body)
        raise TrmnlError(f"HTTP {exc.code}: {decoded}") from exc
    except urllib.error.URLError as exc:
        raise TrmnlError(f"Request failed: {exc}") from exc


def post_webhook(
    webhook_url: str,
    request_body: dict[str, Any],
    *,
    timeout: int = 30,
) -> tuple[int, Any]:
    status, _headers, decoded, _body = request_json(
        webhook_url,
        method="POST",
        payload=request_body,
        timeout=timeout,
    )
    return status, decoded


def fetch_current_screen(
    access_token: str,
    *,
    device_id: str | None = None,
    base_url: str = TRMNL_BASE_URL,
    timeout: int = 30,
) -> tuple[int, dict[str, str], dict[str, Any], bytes]:
    headers = {"access-token": access_token, "Access-Token": access_token}
    if device_id:
        headers["ID"] = device_id
    status, response_headers, decoded, body = request_json(
        f"{base_url.rstrip('/')}/api/current_screen",
        headers=headers,
        timeout=timeout,
    )
    if not isinstance(decoded, dict):
        raise TrmnlError("current_screen response was not a JSON object.")
    return status, response_headers, decoded, body


def download_image(url: str, destination: pathlib.Path, *, timeout: int = 30) -> pathlib.Path:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = response.read()
            content_type = response.headers.get("content-type", "")
    except urllib.error.URLError as exc:
        raise TrmnlError(f"Image download failed: {exc}") from exc

    suffix = ".png"
    if "bmp" in content_type:
        suffix = ".bmp"
    elif "jpeg" in content_type or "jpg" in content_type:
        suffix = ".jpg"
    path = destination.with_suffix(suffix)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def file_digest(path: pathlib.Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}


def summarize_screen_response(
    data: dict[str, Any],
    *,
    image_path: pathlib.Path | None = None,
) -> dict[str, Any]:
    digest = file_digest(image_path) if image_path else {}
    return {
        "trmnl_status": data.get("status"),
        "refresh_rate": data.get("refresh_rate"),
        "filename": data.get("filename") or data.get("image_name"),
        "rendered_at": data.get("rendered_at"),
        "image_url_present": bool(data.get("image_url")),
        "image_saved": str(image_path) if image_path else None,
        "image_sha256": digest.get("sha256"),
        "image_bytes": digest.get("bytes"),
    }


def _decode_body(body: bytes) -> Any:
    if not body:
        return None
    text = body.decode("utf-8", "replace")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text
