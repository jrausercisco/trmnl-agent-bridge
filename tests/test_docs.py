from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class DocumentationTests(unittest.TestCase):
    def test_phase_5_docs_exist(self) -> None:
        required = [
            "README.md",
            "docs/private-plugin-setup.md",
            "docs/codex-plugin.md",
            "docs/claude-plugin.md",
            "docs/payload-contract.md",
            "docs/release-process.md",
            "docs/security.md",
        ]

        for relative in required:
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_readme_links_core_docs(self) -> None:
        text = (ROOT / "README.md").read_text(encoding="utf-8")

        for expected in (
            "docs/private-plugin-setup.md",
            "docs/codex-plugin.md",
            "docs/claude-plugin.md",
            "docs/payload-contract.md",
            "docs/security.md",
        ):
            self.assertIn(expected, text)

    def test_public_docs_do_not_reference_private_workspace_paths(self) -> None:
        docs = [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md"))]
        forbidden = ("/Users/jrauser", "ENDURANCE", "AMOS")

        for path in docs:
            text = path.read_text(encoding="utf-8")
            for item in forbidden:
                self.assertNotIn(item, text, str(path))

    def test_scaffold_language_removed_from_launch_docs(self) -> None:
        docs = [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md"))]
        stale = ("public-ready staging scaffold", "has not been ported", "planned for later phases")

        for path in docs:
            text = path.read_text(encoding="utf-8")
            for item in stale:
                self.assertNotIn(item, text, str(path))


if __name__ == "__main__":
    unittest.main()
