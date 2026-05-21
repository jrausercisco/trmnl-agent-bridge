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

    def test_trmnl_recipe_packaging_files_exist(self) -> None:
        for relative in (
            "trmnl_plugin/plugin.yml",
            "trmnl_plugin/icon.svg",
            "trmnl_plugin/markup_full.html",
            "trmnl_plugin/markup_half_horizontal.html",
            "trmnl_plugin/markup_half_vertical.html",
            "trmnl_plugin/markup_quadrant.html",
        ):
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_trmnl_recipe_markups_use_framework_markup(self) -> None:
        for path in sorted((ROOT / "trmnl_plugin").glob("markup_*.html")):
            template = path.read_text(encoding="utf-8")
            self.assertTrue(template.lstrip().startswith("<div"), str(path))
            self.assertIn('class="layout', template, str(path))
            self.assertIn("{{ state", template, str(path))
            self.assertIn("{{ headline", template, str(path))
            self.assertNotIn("<style", template.lower(), str(path))
            self.assertNotIn("<html", template.lower(), str(path))
            self.assertNotIn("<body", template.lower(), str(path))

    def test_trmnl_full_recipe_matches_canonical_template(self) -> None:
        canonical = (ROOT / "templates" / "agent-status.liquid.html").read_text(encoding="utf-8")
        full_recipe = (ROOT / "trmnl_plugin" / "markup_full.html").read_text(encoding="utf-8")

        self.assertEqual(canonical, full_recipe)

    def test_trmnl_recipe_metadata_is_public_and_copyable(self) -> None:
        metadata = (ROOT / "trmnl_plugin" / "plugin.yml").read_text(encoding="utf-8")
        icon = (ROOT / "trmnl_plugin" / "icon.svg").read_text(encoding="utf-8")

        self.assertIn("copyable_webhook_url", metadata)
        self.assertIn("github.com/jrausercisco/trmnl-agent-bridge", metadata)
        self.assertNotIn("/Users/", metadata)
        self.assertTrue(icon.lstrip().startswith("<svg"))


if __name__ == "__main__":
    unittest.main()
