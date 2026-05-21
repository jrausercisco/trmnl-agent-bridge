from __future__ import annotations

import contextlib
import io
import json
import pathlib
import tempfile
import unittest

from trmnl_agent_bridge.cli import main


class CliTests(unittest.TestCase):
    def test_push_dry_run_with_sample_payload(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = main(["push", "--merge-file", "examples/sample-payload.json", "--dry-run"])

        self.assertEqual(code, 0)
        output = json.loads(stdout.getvalue())
        self.assertTrue(output["dry_run"])
        self.assertEqual(output["request_body"]["merge_variables"]["schema_version"], 1)
        self.assertEqual(output["request_body"]["merge_variables"]["state"], "ACTION")

    def test_preview_with_sample_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            preview_path = pathlib.Path(tmp) / "preview.html"
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["preview", "--merge-file", "examples/sample-payload.json", "--output", str(preview_path)])

            self.assertEqual(code, 0)
            output = json.loads(stdout.getvalue())
            self.assertEqual(output["preview_path"], str(preview_path))
            self.assertIn("Review failed test run", preview_path.read_text(encoding="utf-8"))

    def test_smoke_test_dry_mode_without_credentials(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["--state-dir", tmp, "smoke-test"])

            self.assertEqual(code, 0)
            output = json.loads(stdout.getvalue())
            self.assertEqual(output["mode"], "dry")
            self.assertEqual(output["issues"], [])
            self.assertFalse(output["push"]["attempted"])


if __name__ == "__main__":
    unittest.main()
