from __future__ import annotations

import contextlib
import io
import json
import pathlib
import tempfile
import unittest
from unittest import mock

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

    def test_sample_outputs_payload_that_can_push_from_stdin(self) -> None:
        sample_stdout = io.StringIO()
        with contextlib.redirect_stdout(sample_stdout):
            sample_code = main(["sample", "--source", "claude", "--state", "WATCH"])

        self.assertEqual(sample_code, 0)
        sample_payload = json.loads(sample_stdout.getvalue())
        self.assertEqual(sample_payload["source"], "claude")
        self.assertEqual(sample_payload["state"], "WATCH")

        push_stdout = io.StringIO()
        with mock.patch("sys.stdin", io.StringIO(json.dumps(sample_payload))):
            with contextlib.redirect_stdout(push_stdout):
                push_code = main(["push", "--stdin", "--dry-run"])

        self.assertEqual(push_code, 0)
        output = json.loads(push_stdout.getvalue())
        self.assertEqual(output["request_body"]["merge_variables"]["source"], "claude")
        self.assertEqual(output["request_body"]["merge_variables"]["state"], "WATCH")

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

    def test_preview_supports_recipe_layout_sizes(self) -> None:
        expected = {
            "full": (800, 480),
            "half-horizontal": (800, 240),
            "half-vertical": (400, 480),
            "quadrant": (400, 240),
        }
        with tempfile.TemporaryDirectory() as tmp:
            for layout, (width, height) in expected.items():
                preview_path = pathlib.Path(tmp) / f"{layout}.html"
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout):
                    code = main(
                        [
                            "preview",
                            "--layout",
                            layout,
                            "--merge-file",
                            "examples/sample-payload.json",
                            "--output",
                            str(preview_path),
                        ]
                    )

                self.assertEqual(code, 0, layout)
                output = json.loads(stdout.getvalue())
                self.assertEqual(output["layout"], layout)
                self.assertEqual(output["width"], width)
                self.assertEqual(output["height"], height)
                text = preview_path.read_text(encoding="utf-8")
                self.assertIn(f"width: {width}px;", text)
                self.assertIn(f"height: {height}px;", text)

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
            self.assertEqual(output["preview_layout"], "full")


if __name__ == "__main__":
    unittest.main()
