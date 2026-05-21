from __future__ import annotations

import unittest

from trmnl_agent_bridge.payloads import (
    PayloadError,
    merge_variables_body,
    normalize_payload,
    payload_size_bytes,
)


VALID_PAYLOAD = {
    "schema_version": 1,
    "source": "codex",
    "title": "CODEX NOW",
    "state": "action",
    "headline": "Review failed test run",
    "detail": "One workflow needs attention.",
    "next": "Last run completed 14:12",
    "signals": ["Tests: 1 failed", "PR: ready", "Agent: idle", "Queue: clear", "Extra: ignored"],
    "health": "Dry run OK",
    "updated": "14:13",
}


class PayloadTests(unittest.TestCase):
    def test_normalize_payload_uppercases_state_and_limits_signals(self) -> None:
        payload = normalize_payload(VALID_PAYLOAD)

        self.assertEqual(payload["state"], "ACTION")
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(len(payload["signals"]), 4)
        self.assertEqual(payload["title"], "CODEX NOW")

    def test_normalize_payload_rejects_unknown_fields(self) -> None:
        bad = dict(VALID_PAYLOAD)
        bad["raw_log"] = "private log body"

        with self.assertRaisesRegex(PayloadError, "Unknown payload fields"):
            normalize_payload(bad)

    def test_normalize_payload_requires_schema_version(self) -> None:
        bad = dict(VALID_PAYLOAD)
        bad.pop("schema_version")

        with self.assertRaisesRegex(PayloadError, "Missing required payload fields"):
            normalize_payload(bad)

    def test_merge_variables_body_wraps_payload_for_trmnl_webhook(self) -> None:
        payload = normalize_payload(VALID_PAYLOAD)
        body = merge_variables_body(payload, merge_strategy="deep_merge")

        self.assertEqual(body, {"merge_variables": payload, "merge_strategy": "deep_merge"})
        self.assertLess(payload_size_bytes(payload), 2048)


if __name__ == "__main__":
    unittest.main()
