from __future__ import annotations

import pathlib
import stat
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
            "docs/release-notes-v0.1.0.md",
            "docs/release-notes-v0.1.1.md",
            "docs/release-notes-v0.1.2.md",
            "docs/launch-post.md",
            "docs/value.md",
            "docs/producer-examples.md",
            "docs/security.md",
            "docs/assets/synthetic-preview.svg",
            "examples/github-actions-agent-status.yml",
            "examples/cron-agent-status.sh",
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
            "docs/value.md",
            "docs/producer-examples.md",
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

    def test_readme_has_demo_image_and_positioning_faq(self) -> None:
        text = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("docs/assets/synthetic-preview.svg", text)
        self.assertIn("Is this a Claude usage dashboard?", text)
        self.assertIn("Does it read prompts or local session files?", text)
        self.assertIn("Why include recipe layout files?", text)
        self.assertIn("Why Use It?", text)
        self.assertIn("Why not just ask an agent to build a custom one?", text)

    def test_value_doc_explains_reuse_over_one_off_generation(self) -> None:
        text = (ROOT / "docs" / "value.md").read_text(encoding="utf-8")

        for expected in (
            "Why Not Just Ask An Agent To Build One?",
            "stable payload contract",
            "credential redaction",
            "TRMNL recipe packaging",
            "GitHub Actions and cron examples",
        ):
            self.assertIn(expected, text)

    def test_producer_examples_are_safe_and_copyable(self) -> None:
        workflow = (ROOT / "examples" / "github-actions-agent-status.yml").read_text(encoding="utf-8")
        cron = (ROOT / "examples" / "cron-agent-status.sh").read_text(encoding="utf-8")
        docs = (ROOT / "docs" / "producer-examples.md").read_text(encoding="utf-8")

        self.assertIn("TRMNL_WEBHOOK_URL: ${{ secrets.TRMNL_WEBHOOK_URL }}", workflow)
        self.assertIn("trmnl-agent push --merge-file trmnl-status.json", workflow)
        self.assertIn("workflow_dispatch", workflow)
        self.assertNotIn("https://trmnl.com/api/custom_plugins", workflow)

        self.assertIn("Usage: cron-agent-status.sh [--dry-run|--push]", cron)
        self.assertIn("trmnl-agent push --merge-file", cron)
        self.assertIn("--dry-run", cron)
        self.assertNotIn("https://trmnl.com/api/custom_plugins", cron)
        self.assertTrue((ROOT / "examples" / "cron-agent-status.sh").stat().st_mode & stat.S_IXUSR)

        self.assertIn("examples/github-actions-agent-status.yml", docs)
        self.assertIn("examples/cron-agent-status.sh", docs)
        self.assertIn("does not include command output", docs)

    def test_scaffold_language_removed_from_launch_docs(self) -> None:
        docs = [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md"))]
        stale = ("public-ready staging scaffold", "has not been ported", "planned for later phases")

        for path in docs:
            text = path.read_text(encoding="utf-8")
            for item in stale:
                self.assertNotIn(item, text, str(path))

    def test_private_plugin_setup_documents_webhook_pitfalls(self) -> None:
        text = (ROOT / "docs/private-plugin-setup.md").read_text(encoding="utf-8")

        for expected in (
            "First Webhook Checklist",
            "Common Setup Pitfalls",
            "Private Plugin strategy is `Webhook`",
            "pbcopy < templates/agent-status.liquid.html",
            "trmnl-agent keychain-set --account TRMNL_WEBHOOK_URL",
            "The webhook URL is only for data updates.",
        ):
            self.assertIn(expected, text)

    def test_plugin_setup_skills_use_installed_user_first_run_flow(self) -> None:
        setup_paths = [
            ROOT / "plugins" / "trmnl-agent-bridge" / "skills" / "setup" / "SKILL.md",
            ROOT / "plugins" / "claude" / "trmnl-agent-bridge" / "skills" / "setup" / "SKILL.md",
        ]

        for path in setup_paths:
            text = path.read_text(encoding="utf-8")
            self.assertIn("choose the `Webhook` data strategy", text)
            self.assertIn("trmnl-agent sample --source", text)
            self.assertIn("trmnl_plugin/markup_full.html", text)


if __name__ == "__main__":
    unittest.main()
