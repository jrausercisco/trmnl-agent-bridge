from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class ReleaseHardeningTests(unittest.TestCase):
    def test_secret_scan_script_exists_and_is_wired_into_release_validation(self) -> None:
        secret_scan = ROOT / "scripts" / "secret-scan.sh"
        validate_release = (ROOT / "scripts" / "validate-release.sh").read_text(encoding="utf-8")

        self.assertTrue(secret_scan.is_file())
        self.assertIn("./scripts/secret-scan.sh", validate_release)

    def test_ci_runs_release_validation_and_secret_scan(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

        self.assertIn("./scripts/validate-release.sh", workflow)
        self.assertIn("./scripts/secret-scan.sh", workflow)
        self.assertIn("actions/checkout@v6", workflow)
        self.assertIn("actions/setup-python@v6", workflow)

    def test_community_files_exist(self) -> None:
        for relative in (
            "CONTRIBUTING.md",
            "CODE_OF_CONDUCT.md",
            "SECURITY.md",
            ".github/ISSUE_TEMPLATE/bug_report.yml",
            ".github/ISSUE_TEMPLATE/feature_request.yml",
            ".github/ISSUE_TEMPLATE/config.yml",
        ):
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_security_docs_reference_private_reporting_and_secret_scan(self) -> None:
        security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
        docs_security = (ROOT / "docs" / "security.md").read_text(encoding="utf-8")

        self.assertIn("security/advisories/new", security)
        self.assertIn("./scripts/secret-scan.sh", docs_security)


if __name__ == "__main__":
    unittest.main()
