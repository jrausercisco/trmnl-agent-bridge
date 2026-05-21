"""Command-line interface for TRMNL agent bridge."""

from __future__ import annotations

import argparse
import getpass
import json
import pathlib
import sys
import time
from typing import Any

from . import __version__
from .credentials import (
    KEYCHAIN_ACCOUNTS,
    KEYCHAIN_SERVICE,
    CredentialError,
    keychain_store,
    redact_secret,
    resolve_credential,
)
from .payloads import (
    DEFAULT_PAYLOAD_LIMIT_BYTES,
    PayloadError,
    default_payload,
    json_bytes,
    load_json_text,
    merge_variables_body,
    normalize_payload,
    payload_size_bytes,
)
from .preview import render_preview
from .trmnl import (
    TRMNL_BASE_URL,
    TrmnlError,
    download_image,
    fetch_current_screen,
    post_webhook,
    summarize_screen_response,
)


DEFAULT_STATE_DIR = pathlib.Path("~/.trmnl-agent-bridge").expanduser()
DEFAULT_PUSH_LIMIT_PER_HOUR = 12


class CliError(RuntimeError):
    """Expected CLI failure."""


def command_status(args: argparse.Namespace) -> int:
    state_dir = _ensure_state_dir(args)
    last_push = _read_json_if_exists(state_dir / "last-push.json") or {}
    credentials = _credential_summary(args)
    print(
        json.dumps(
            {
                "ok": True,
                "version": __version__,
                "state_dir": str(state_dir),
                "keychain_service": KEYCHAIN_SERVICE,
                "credentials": credentials,
                "can_push_private_plugin": credentials["webhook_url"]["source"] != "missing",
                "can_fetch_current_screen": credentials["access_token"]["source"] != "missing",
                "last_push": last_push,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def command_setup(args: argparse.Namespace) -> int:
    print(
        "\n".join(
            [
                "TRMNL Agent Bridge setup",
                "",
                "1. Create a TRMNL Private Plugin and choose webhook-based updates.",
                "2. Paste templates/agent-status.liquid.html into the plugin markup.",
                "3. Store the webhook URL as TRMNL_WEBHOOK_URL or in macOS Keychain:",
                "   trmnl-agent keychain-set --account TRMNL_WEBHOOK_URL",
                "4. Dry-run a payload:",
                "   trmnl-agent push --merge-file examples/sample-payload.json --dry-run",
                "5. Push when ready:",
                "   trmnl-agent push --merge-file examples/sample-payload.json",
            ]
        )
    )
    return 0


def command_keychain_set(args: argparse.Namespace) -> int:
    if args.value and args.value_stdin:
        raise CliError("Use either --value or --value-stdin, not both.")
    if args.value_stdin:
        value = sys.stdin.read().strip()
    elif args.value:
        value = args.value
    else:
        value = getpass.getpass(f"{args.account}: ").strip()
    if not value:
        raise CliError(f"No value provided for {args.account}.")
    keychain_store(args.account, value)
    print(json.dumps({"ok": True, "account": args.account, "source": "keychain"}, indent=2))
    return 0


def command_push(args: argparse.Namespace) -> int:
    state_dir = _ensure_state_dir(args)
    payload = _load_payload_from_args(args)
    request_body = merge_variables_body(
        payload,
        merge_strategy=args.merge_strategy,
        stream_limit=args.stream_limit,
    )
    payload_bytes = payload_size_bytes(payload)
    request_bytes = len(json_bytes(request_body))
    within_limit = payload_bytes <= args.payload_limit_bytes
    if not within_limit:
        raise CliError(
            f"Payload is {payload_bytes} bytes, exceeding limit {args.payload_limit_bytes} bytes."
        )

    webhook = resolve_credential(args.webhook_url, "TRMNL_WEBHOOK_URL")
    output: dict[str, Any] = {
        "ok": True,
        "dry_run": bool(args.dry_run),
        "payload_bytes": payload_bytes,
        "request_bytes": request_bytes,
        "payload_limit_bytes": args.payload_limit_bytes,
        "webhook_url_source": webhook.source,
        "state": payload.get("state"),
        "headline": payload.get("headline"),
    }

    if args.dry_run:
        output["request_body"] = request_body
        print(json.dumps(output, indent=2, sort_keys=True))
        return 0

    if not webhook.value:
        raise CliError("Missing TRMNL_WEBHOOK_URL. Set it in the environment, Keychain, or --webhook-url.")

    _check_push_limit(state_dir, args.limit_per_hour)
    status, response = post_webhook(webhook.value, request_body, timeout=args.timeout)
    metadata = {
        "pushed_at": int(time.time()),
        "http_status": status,
        "payload_sha256": _sha256_json(payload),
        "payload_bytes": payload_bytes,
        "state": payload.get("state"),
        "headline": payload.get("headline"),
    }
    _write_json(state_dir / "last-push.json", metadata)
    output.update(
        {
            "http_status": status,
            "response_present": response is not None,
            "response_type": type(response).__name__ if response is not None else None,
            "last_push_path": str(state_dir / "last-push.json"),
        }
    )
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


def command_preview(args: argparse.Namespace) -> int:
    state_dir = _ensure_state_dir(args)
    payload = _load_payload_from_args(args, allow_default=True)
    destination = pathlib.Path(args.output).expanduser() if args.output else state_dir / "agent-status-preview.html"
    preview_path = render_preview(payload, destination)
    print(
        json.dumps(
            {
                "ok": True,
                "preview_path": str(preview_path),
                "payload_bytes": payload_size_bytes(payload),
                "state": payload.get("state"),
                "headline": payload.get("headline"),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def command_current_screen(args: argparse.Namespace) -> int:
    state_dir = _ensure_state_dir(args)
    access_token = resolve_credential(args.access_token, "TRMNL_ACCESS_TOKEN")
    device_id = resolve_credential(args.device_id, "TRMNL_DEVICE_ID")
    if not access_token.value:
        raise CliError("Missing TRMNL_ACCESS_TOKEN. Set it in the environment, Keychain, or --access-token.")

    status, _headers, data, _body = fetch_current_screen(
        access_token.value,
        device_id=device_id.value,
        base_url=args.base_url,
        timeout=args.timeout,
    )
    image_path = None
    if args.download_image and data.get("image_url"):
        image_path = download_image(str(data["image_url"]), state_dir / "current-screen", timeout=args.timeout)
    summary = summarize_screen_response(data, image_path=image_path)
    summary.update({"ok": 200 <= status < 300, "http_status": status})
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def command_smoke_test(args: argparse.Namespace) -> int:
    state_dir = _ensure_state_dir(args)
    payload = _load_payload_from_args(args, allow_default=True)
    preview_path = render_preview(payload, pathlib.Path(args.output).expanduser() if args.output else state_dir / "agent-status-preview.html")
    webhook = resolve_credential(args.webhook_url, "TRMNL_WEBHOOK_URL")
    access_token = resolve_credential(args.access_token, "TRMNL_ACCESS_TOKEN")
    device_id = resolve_credential(args.device_id, "TRMNL_DEVICE_ID")
    request_body = merge_variables_body(payload)
    issues: list[str] = []
    payload_bytes = payload_size_bytes(payload)
    if payload_bytes > args.payload_limit_bytes:
        issues.append(f"payload exceeds {args.payload_limit_bytes} bytes")
    if args.push and not webhook.value:
        issues.append("TRMNL_WEBHOOK_URL is missing")
    if args.fetch_screen and not access_token.value:
        issues.append("TRMNL_ACCESS_TOKEN is missing")

    result: dict[str, Any] = {
        "ok": not issues,
        "mode": "live" if args.push else "dry",
        "issues": issues,
        "preview_path": str(preview_path),
        "payload_bytes": payload_bytes,
        "payload_limit_bytes": args.payload_limit_bytes,
        "state": payload.get("state"),
        "headline": payload.get("headline"),
        "credential_sources": _credential_summary(args),
    }

    before = None
    if args.compare_screen and args.fetch_screen and args.push and access_token.value:
        before = _safe_current_screen(
            access_token.value,
            device_id.value,
            state_dir / "screen-before",
            args,
            download=True,
        )
        result["screen_before"] = before
        result["ok"] = bool(result["ok"] and before.get("ok"))

    if args.push and webhook.value and not issues:
        _check_push_limit(state_dir, args.limit_per_hour)
        try:
            status, response = post_webhook(webhook.value, request_body, timeout=args.timeout)
            result["push"] = {
                "attempted": True,
                "ok": 200 <= status < 300,
                "http_status": status,
                "response_present": response is not None,
                "response_type": type(response).__name__ if response is not None else None,
            }
            result["ok"] = bool(result["ok"] and result["push"]["ok"])
        except TrmnlError as exc:
            result["push"] = {"attempted": True, "ok": False, "error": str(exc)}
            result["ok"] = False
    else:
        result["push"] = {"attempted": False, "reason": "dry mode" if not args.push else "not ready"}

    if args.fetch_screen and access_token.value:
        if args.wait_seconds:
            time.sleep(args.wait_seconds)
        screen = _safe_current_screen(
            access_token.value,
            device_id.value,
            state_dir / "screen-after",
            args,
            download=bool(args.download_image or args.compare_screen),
        )
        result["screen"] = screen
        result["ok"] = bool(result["ok"] and screen.get("ok"))
        if before:
            result["screen_changed"] = bool(
                before.get("image_sha256")
                and screen.get("image_sha256")
                and before.get("image_sha256") != screen.get("image_sha256")
            )

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("ok") else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Publish local agent status to TRMNL Private Plugin webhooks.")
    parser.add_argument("--webhook-url", help="TRMNL Private Plugin webhook URL. Env: TRMNL_WEBHOOK_URL.")
    parser.add_argument("--access-token", help="TRMNL device API key. Env: TRMNL_ACCESS_TOKEN.")
    parser.add_argument("--device-id", help="Optional TRMNL device ID/MAC. Env: TRMNL_DEVICE_ID.")
    parser.add_argument("--state-dir", default=str(DEFAULT_STATE_DIR), help="Local state/output directory.")
    parser.add_argument("--base-url", default=TRMNL_BASE_URL, help="TRMNL base URL for device API calls.")
    parser.add_argument("--timeout", type=int, default=30, help="HTTP timeout in seconds.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    status = subparsers.add_parser("status", help="Show configuration and credential sources with redaction.")
    status.set_defaults(func=command_status)

    setup = subparsers.add_parser("setup", help="Print the Private Plugin setup checklist.")
    setup.set_defaults(func=command_setup)

    keychain_set = subparsers.add_parser("keychain-set", help="Store one TRMNL credential in macOS Keychain.")
    keychain_set.add_argument("--account", required=True, choices=KEYCHAIN_ACCOUNTS)
    keychain_set.add_argument("--value", help="Credential value. Prefer prompt or --value-stdin for secrets.")
    keychain_set.add_argument("--value-stdin", action="store_true", help="Read the credential value from stdin.")
    keychain_set.set_defaults(func=command_keychain_set)

    push = subparsers.add_parser("push", help="Validate and push an agent-status payload.")
    _add_payload_args(push)
    push.add_argument("--dry-run", action="store_true", help="Validate and print the webhook body without sending it.")
    push.add_argument("--merge-strategy", choices=["deep_merge", "stream"], help="Optional TRMNL merge strategy.")
    push.add_argument("--stream-limit", type=int, help="Optional TRMNL stream_limit value.")
    push.add_argument("--payload-limit-bytes", type=int, default=DEFAULT_PAYLOAD_LIMIT_BYTES)
    push.add_argument("--limit-per-hour", type=int, default=DEFAULT_PUSH_LIMIT_PER_HOUR)
    push.set_defaults(func=command_push)

    preview = subparsers.add_parser("preview", help="Render a local 800x480 HTML preview.")
    _add_payload_args(preview)
    preview.add_argument("--output", help="Preview HTML output path.")
    preview.set_defaults(func=command_preview)

    current_screen = subparsers.add_parser("current-screen", help="Fetch current TRMNL screen metadata.")
    current_screen.add_argument("--download-image", action="store_true", help="Download current-screen image for hashing.")
    current_screen.set_defaults(func=command_current_screen)

    smoke = subparsers.add_parser("smoke-test", help="Dry-run or live-test payload, preview, push, and screen fetch.")
    _add_payload_args(smoke)
    smoke.add_argument("--output", help="Preview HTML output path.")
    smoke.add_argument("--push", action="store_true", help="Send the payload when TRMNL_WEBHOOK_URL is available.")
    smoke.add_argument("--fetch-screen", action="store_true", help="Fetch current-screen metadata.")
    smoke.add_argument("--compare-screen", action="store_true", help="Hash before/after screen images around a live push.")
    smoke.add_argument("--download-image", action="store_true", help="Download current-screen image when fetching.")
    smoke.add_argument("--wait-seconds", type=int, default=0, help="Delay before fetching the post-push screen.")
    smoke.add_argument("--payload-limit-bytes", type=int, default=DEFAULT_PAYLOAD_LIMIT_BYTES)
    smoke.add_argument("--limit-per-hour", type=int, default=DEFAULT_PUSH_LIMIT_PER_HOUR)
    smoke.set_defaults(func=command_smoke_test)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (CliError, CredentialError, PayloadError, TrmnlError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def _add_payload_args(parser: argparse.ArgumentParser) -> None:
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--merge-file", help="Path to agent-status JSON.")
    group.add_argument("--merge-json", help="Inline agent-status JSON object.")
    group.add_argument("--stdin", action="store_true", help="Read agent-status JSON from stdin.")


def _load_payload_from_args(args: argparse.Namespace, *, allow_default: bool = False) -> dict[str, Any]:
    if getattr(args, "merge_file", None):
        text = pathlib.Path(args.merge_file).expanduser().read_text(encoding="utf-8")
        return normalize_payload(load_json_text(text))
    if getattr(args, "merge_json", None):
        return normalize_payload(load_json_text(args.merge_json))
    if getattr(args, "stdin", False):
        return normalize_payload(load_json_text(sys.stdin.read()))
    if allow_default:
        return default_payload()
    raise CliError("Provide --merge-file, --merge-json, or --stdin.")


def _ensure_state_dir(args: argparse.Namespace) -> pathlib.Path:
    state_dir = pathlib.Path(args.state_dir).expanduser()
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir


def _credential_summary(args: argparse.Namespace) -> dict[str, dict[str, str]]:
    webhook = resolve_credential(getattr(args, "webhook_url", None), "TRMNL_WEBHOOK_URL")
    access_token = resolve_credential(getattr(args, "access_token", None), "TRMNL_ACCESS_TOKEN")
    device_id = resolve_credential(getattr(args, "device_id", None), "TRMNL_DEVICE_ID")
    return {
        "webhook_url": {"source": webhook.source, "value": redact_secret(webhook.value)},
        "access_token": {"source": access_token.source, "value": redact_secret(access_token.value)},
        "device_id": {"source": device_id.source, "value": redact_secret(device_id.value)},
    }


def _check_push_limit(state_dir: pathlib.Path, limit_per_hour: int) -> None:
    path = state_dir / "push-history.json"
    now = time.time()
    history: list[float] = []
    if path.exists():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(loaded, list):
                history = [float(item) for item in loaded]
        except Exception:
            history = []
    history = [item for item in history if now - item < 3600]
    if len(history) >= limit_per_hour:
        raise CliError(f"Push limit would exceed {limit_per_hour}/hour.")
    history.append(now)
    _write_json(path, history)


def _safe_current_screen(
    access_token: str,
    device_id: str | None,
    destination: pathlib.Path,
    args: argparse.Namespace,
    *,
    download: bool,
) -> dict[str, Any]:
    try:
        status, _headers, data, _body = fetch_current_screen(
            access_token,
            device_id=device_id,
            base_url=args.base_url,
            timeout=args.timeout,
        )
        image_path = None
        if download and data.get("image_url"):
            image_path = download_image(str(data["image_url"]), destination, timeout=args.timeout)
        summary = summarize_screen_response(data, image_path=image_path)
        summary.update({"ok": 200 <= status < 300, "http_status": status})
        return summary
    except TrmnlError as exc:
        return {"ok": False, "error": str(exc)}


def _write_json(path: pathlib.Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


def _read_json_if_exists(path: pathlib.Path) -> Any | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _sha256_json(value: Any) -> str:
    import hashlib

    return hashlib.sha256(json_bytes(value)).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
