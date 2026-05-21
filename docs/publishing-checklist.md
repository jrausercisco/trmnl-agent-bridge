# Publishing Checklist

Use this checklist before making the repository public.

- [ ] Confirm no private workflow names or local paths appear in public docs.
- [ ] Confirm no webhook URLs, device IDs, API tokens, response JSON, or screenshots are committed.
- [ ] Confirm sample payloads contain only synthetic data.
- [x] Confirm the README clearly says whether the CLI is implemented.
- [ ] Confirm the license is intentional.
- [x] Confirm the package name and repository URL are final.
- [x] Confirm the TRMNL template renders with the sample payload.
- [x] Add tests before porting non-trivial bridge code.
- [x] Add Codex plugin manifest, skills, marketplace metadata, and validation coverage.
- [x] Validate repo-local Codex marketplace discovery with an isolated Codex home.
- [x] Add Claude Code plugin manifest, skills, marketplace metadata, and validation coverage.
- [x] Validate Claude marketplace and plugin directory with `claude plugin validate`.
- [x] Validate Claude marketplace registration and local plugin install with an isolated Claude home.
- [x] Rewrite README as a launch-ready first-time flow.
- [x] Add payload contract and release process docs.
- [x] Add documentation validation coverage for Phase 5 docs.
- [x] Add release hardening files, issue templates, CI workflow, and security reporting docs.
- [x] Run the local secret scan before the first push.
- [x] Confirm GitHub Actions CI passes after the first public push.
- [x] Verify GitHub-hosted Codex marketplace add flow.
- [x] Verify GitHub-hosted Claude marketplace add and install flow.
- [x] Draft `v0.1.0` release notes.
- [ ] Tag the first release only after a real CLI smoke test passes.
