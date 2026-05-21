from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
CODEX_PLUGIN_ROOT = ROOT / "plugins" / "trmnl-agent-bridge"
CLAUDE_PLUGIN_ROOT = ROOT / "plugins" / "claude" / "trmnl-agent-bridge"


class PluginManifestTests(unittest.TestCase):
    def test_codex_plugin_manifest_references_existing_skills(self) -> None:
        manifest_path = CODEX_PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        self.assertEqual(manifest["name"], "trmnl-agent-bridge")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertTrue((CODEX_PLUGIN_ROOT / "skills").is_dir())
        self.assertNotIn("[TODO:", json.dumps(manifest))

    def test_codex_marketplace_points_to_plugin(self) -> None:
        marketplace_path = ROOT / ".agents" / "plugins" / "marketplace.json"
        marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))

        entries = marketplace["plugins"]
        self.assertEqual(len(entries), 1)
        entry = entries[0]
        self.assertEqual(entry["name"], "trmnl-agent-bridge")
        self.assertEqual(entry["source"], {"source": "local", "path": "./plugins/trmnl-agent-bridge"})
        self.assertEqual(entry["policy"]["installation"], "AVAILABLE")
        self.assertEqual(entry["policy"]["authentication"], "ON_INSTALL")
        self.assertTrue((ROOT / entry["source"]["path"]).is_dir())

    def test_codex_skills_have_frontmatter_and_required_files(self) -> None:
        skill_names = {"publish-status", "setup", "smoke-test"}
        skill_paths = {path.parent.name: path for path in CODEX_PLUGIN_ROOT.glob("skills/*/SKILL.md")}

        self.assertEqual(set(skill_paths), skill_names)
        for name, path in skill_paths.items():
            text = path.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---\n"), name)
            self.assertIn(f"name: {name}", text)
            self.assertIn("description:", text)
            self.assertIn("trmnl-agent", text)

    def test_claude_plugin_manifest_references_existing_skills(self) -> None:
        manifest_path = CLAUDE_PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        self.assertEqual(manifest["name"], "trmnl-agent-bridge")
        self.assertEqual(manifest["displayName"], "TRMNL Agent Bridge")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertTrue((CLAUDE_PLUGIN_ROOT / "skills").is_dir())
        self.assertNotIn("[TODO:", json.dumps(manifest))

    def test_claude_marketplace_points_to_plugin(self) -> None:
        marketplace_path = ROOT / ".claude-plugin" / "marketplace.json"
        marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))

        self.assertEqual(marketplace["name"], "trmnl-agent-bridge")
        self.assertEqual(marketplace["owner"]["name"], "John Rauser")
        entries = marketplace["plugins"]
        self.assertEqual(len(entries), 1)
        entry = entries[0]
        self.assertEqual(entry["name"], "trmnl-agent-bridge")
        self.assertEqual(entry["source"], "./plugins/claude/trmnl-agent-bridge")
        self.assertTrue((ROOT / entry["source"]).is_dir())

    def test_claude_skills_have_frontmatter_and_required_files(self) -> None:
        skill_names = {"publish-status", "setup", "smoke-test"}
        skill_paths = {path.parent.name: path for path in CLAUDE_PLUGIN_ROOT.glob("skills/*/SKILL.md")}

        self.assertEqual(set(skill_paths), skill_names)
        for name, path in skill_paths.items():
            text = path.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---\n"), name)
            self.assertIn("description:", text)
            self.assertIn("trmnl-agent", text)


if __name__ == "__main__":
    unittest.main()
