from __future__ import annotations

import unittest

from trmnl_agent_bridge.trmnl import summarize_screen_response


class TrmnlTests(unittest.TestCase):
    def test_summarize_screen_response_hides_image_url(self) -> None:
        summary = summarize_screen_response(
            {
                "status": 200,
                "refresh_rate": 1800,
                "image_url": "https://trmnl.example/private-image.png",
                "filename": "plugin-demo",
                "rendered_at": None,
            }
        )

        self.assertTrue(summary["image_url_present"])
        self.assertNotIn("image_url", summary)
        self.assertEqual(summary["filename"], "plugin-demo")


if __name__ == "__main__":
    unittest.main()
