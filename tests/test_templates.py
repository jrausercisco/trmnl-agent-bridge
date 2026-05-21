from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class TemplateTests(unittest.TestCase):
    def test_agent_status_template_uses_trmnl_framework_markup(self) -> None:
        template = (ROOT / "templates" / "agent-status.liquid.html").read_text(encoding="utf-8")

        self.assertIn('class="layout', template)
        self.assertIn('class="item', template)
        self.assertIn("{{ headline", template)
        self.assertNotIn("<style", template.lower())
        self.assertNotIn("<html", template.lower())
        self.assertNotIn("<body", template.lower())

    def test_agent_status_template_starts_with_html_not_bare_liquid(self) -> None:
        template = (ROOT / "templates" / "agent-status.liquid.html").read_text(encoding="utf-8")

        self.assertTrue(template.lstrip().startswith("<div"), "template should be copied as raw markup")


if __name__ == "__main__":
    unittest.main()
