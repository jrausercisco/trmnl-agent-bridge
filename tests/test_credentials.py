from __future__ import annotations

import unittest
from unittest import mock

from trmnl_agent_bridge import credentials


class CredentialTests(unittest.TestCase):
    def test_resolve_credential_prefers_explicit_value(self) -> None:
        with mock.patch.dict("os.environ", {"TRMNL_WEBHOOK_URL": "https://env.example"}):
            resolved = credentials.resolve_credential("https://arg.example", "TRMNL_WEBHOOK_URL", use_keychain=False)

        self.assertEqual(resolved.value, "https://arg.example")
        self.assertEqual(resolved.source, "argument")

    def test_resolve_credential_uses_environment(self) -> None:
        with mock.patch.dict("os.environ", {"TRMNL_WEBHOOK_URL": "https://env.example"}):
            resolved = credentials.resolve_credential(None, "TRMNL_WEBHOOK_URL", use_keychain=False)

        self.assertEqual(resolved.value, "https://env.example")
        self.assertEqual(resolved.source, "environment")

    def test_resolve_credential_uses_keychain(self) -> None:
        with mock.patch.dict("os.environ", {}, clear=True):
            with mock.patch.object(credentials, "keychain_lookup", return_value="https://keychain.example"):
                resolved = credentials.resolve_credential(None, "TRMNL_WEBHOOK_URL")

        self.assertEqual(resolved.value, "https://keychain.example")
        self.assertEqual(resolved.source, "keychain")

    def test_redact_secret_never_prints_full_value(self) -> None:
        self.assertEqual(credentials.redact_secret(None), "<missing>")
        self.assertEqual(credentials.redact_secret("abcd"), "<set>")
        self.assertEqual(credentials.redact_secret("https://secret.example/path"), "http...path")


if __name__ == "__main__":
    unittest.main()
