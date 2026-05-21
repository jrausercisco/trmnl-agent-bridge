# End-To-End Build And Publishing Plan

Status: Phase 0-2 implemented locally; plugin bundles pending  
Target audience: TRMNL users who run Codex, Claude Code, local agents, scripts, CI, or homelab automations  
Current repo state: renamed local MVP with CLI, schema, preview, smoke test, and tests  
Public name: `trmnl-agent-bridge`

## Goal

Build and publish a generic TRMNL agent-status bridge that works well with both Codex and Claude Code.

The public project should give any TRMNL user a repeatable way to show calm, compact status from local agent workflows on an e-ink screen. Codex and Claude Code are first-class integrations, but the core should work with any JSON-producing tool.

## Product Definition

This project has three related deliverables:

1. A local CLI: `trmnl-agent`
   - Loads a compact agent-status payload from JSON, stdin, or a command.
   - Validates and normalizes the payload.
   - Pushes it to a TRMNL Private Plugin webhook.
   - Provides setup, preview, status, and smoke-test commands.

2. A Codex plugin bundle
   - Packages a Codex plugin manifest at `.codex-plugin/plugin.json`.
   - Provides skills that tell Codex how to summarize its current run, prepare safe TRMNL payloads, and invoke the CLI.
   - Ships through a Codex marketplace entry in `.agents/plugins/marketplace.json`.

3. A Claude Code plugin bundle
   - Packages a Claude plugin manifest at `.claude-plugin/plugin.json`.
   - Provides equivalent skills for Claude Code.
   - Ships through a Claude marketplace file at `.claude-plugin/marketplace.json`.

The TRMNL side is not a hosted service. The default display endpoint is a TRMNL Private Plugin using webhook `merge_variables`. Once the project is stable, the template can also be submitted as a TRMNL Recipe so users can install the display layout more easily.

## Naming Decision

Rename before the first public push.

Recommended:

- Repository: `trmnl-agent-bridge`
- Python package: `trmnl-agent-bridge`
- CLI command: `trmnl-agent`
- Codex plugin name: `trmnl-agent-bridge`
- Claude plugin name: `trmnl-agent-bridge`
- Backward-compatible CLI alias: `trmnl-codex`, optional and deprecated from day one

Reason: the previous `trmnl-codex-bridge` staging name was too narrow for a world-facing plugin that supports both Codex and Claude Code.

2026-05-21 implementation note: the local repo directory, package references, README, sample payloads, and template were renamed to `trmnl-agent-bridge`. The `trmnl-agent` CLI is now the primary command, while `trmnl-codex` remains only as a deprecated compatibility alias.

## Source Assumptions Checked

- TRMNL Private Plugin webhooks accept POST payloads under a `merge_variables` node and expose those variables to the Markup Editor.
- TRMNL supports different custom plugin types; Private Plugin is the lowest-friction local-first path, Recipe is the lightweight public-sharing path, and Third Party Plugin is the hosted/OAuth path.
- Codex plugins use `.codex-plugin/plugin.json`; published plugins commonly include richer metadata, skills, optional hooks, and marketplace metadata.
- Claude Code plugins use `.claude-plugin/plugin.json`; Claude marketplace catalogs live at `.claude-plugin/marketplace.json`, and users can add GitHub-hosted marketplaces.
- Both ecosystems support skills as the right cross-agent abstraction for "teach the agent how to create and publish a safe status update."

Primary references:

- TRMNL webhooks: https://docs.trmnl.com/go/private-plugins/webhooks
- TRMNL custom plugin types: https://help.trmnl.com/en/articles/10546870-compare-custom-plugin-types
- Codex plugin build docs: https://developers.openai.com/codex/plugins/build
- Claude plugin creation docs: https://code.claude.com/docs/en/plugins
- Claude marketplace docs: https://code.claude.com/docs/en/plugin-marketplaces
- Claude plugin reference: https://code.claude.com/docs/en/plugins-reference

## Target User Experience

### TRMNL Setup

```bash
pipx install git+https://github.com/<owner>/trmnl-agent-bridge.git
trmnl-agent setup
trmnl-agent keychain-set --account TRMNL_WEBHOOK_URL
trmnl-agent push --merge-file examples/sample-payload.json
trmnl-agent smoke-test --push --fetch-screen --compare-screen
```

### Codex Setup

```bash
codex plugin marketplace add <owner>/trmnl-agent-bridge
```

Then install or enable `trmnl-agent-bridge` from the Codex plugin directory. The README should verify the exact Codex CLI install command before launch because current Codex docs emphasize marketplace add, plugin-directory browsing, and marketplace metadata while official self-serve directory publishing is still marked as coming soon.

Expected Codex prompts:

```text
Use the trmnl-agent-bridge skill to publish the current run status to TRMNL.
Use the trmnl-agent-bridge skill to show that this task is blocked and needs review.
```

### Claude Code Setup

```bash
claude plugin marketplace add <owner>/trmnl-agent-bridge
claude plugin install trmnl-agent-bridge@trmnl-agent-bridge
```

Expected Claude prompts:

```text
/trmnl-agent-bridge:publish-status
/trmnl-agent-bridge:setup
```

## Repository Architecture

Target structure after the rename:

```text
trmnl-agent-bridge/
  README.md
  LICENSE
  SECURITY.md
  pyproject.toml
  src/trmnl_agent_bridge/
    __init__.py
    cli.py
    credentials.py
    payloads.py
    trmnl.py
    preview.py
  schemas/
    agent-status.v1.schema.json
  templates/
    agent-status.liquid.html
  examples/
    sample-payload.json
    sample-codex-status.json
    sample-claude-status.json
    codex-automation-prompt.md
    claude-automation-prompt.md
  plugins/
    trmnl-agent-bridge/
      .codex-plugin/plugin.json
      skills/publish-status/SKILL.md
      skills/setup/SKILL.md
      skills/smoke-test/SKILL.md
    claude/trmnl-agent-bridge/
      .claude-plugin/plugin.json
      skills/publish-status/SKILL.md
      skills/setup/SKILL.md
      skills/smoke-test/SKILL.md
  .agents/plugins/
    marketplace.json
  .claude-plugin/
    marketplace.json
  docs/
    end-to-end-build-and-publishing-plan.md
    private-plugin-setup.md
    security.md
    publishing-checklist.md
    codex-plugin.md
    claude-plugin.md
    payload-contract.md
    release-process.md
  tests/
    test_credentials.py
    test_payloads.py
    test_trmnl.py
    test_cli.py
    test_plugin_manifests.py
  scripts/
    sync-plugin-skills.py
    secret-scan.sh
    validate-release.sh
```

The Codex and Claude plugin directories must be self-contained. Do not rely on `../shared` files at install time because plugin installers may copy or cache plugin directories independently.

## Payload Contract

Create `schemas/agent-status.v1.schema.json` and make it the stable public contract.

Required fields:

- `schema_version`: `1`
- `source`: short producer name such as `codex`, `claude`, `github-actions`, or `cron`
- `state`: `CLEAR`, `WATCH`, `ACTION`, `BLOCKED`, or `FAIL`
- `headline`: one display-sized status line
- `detail`: one sentence of context
- `updated`: local display time or ISO timestamp

Optional fields:

- `title`
- `next`
- `signals`
- `health`
- `run_url`
- `repo`
- `branch`
- `task`
- `expires_at`

Privacy rule: the schema should support useful status without requiring prompts, transcripts, private note bodies, customer names, emails, or raw logs.

## CLI Command Plan

### MVP Commands

- `trmnl-agent status`
  - Shows version, credential source availability, last payload hash, and last push time.
  - Redacts secrets.

- `trmnl-agent setup`
  - Prints the Private Plugin setup checklist.
  - Optionally writes a local `.env.example`.

- `trmnl-agent keychain-set --account TRMNL_WEBHOOK_URL`
  - Stores webhook URL in macOS Keychain.
  - Later: add Linux Secret Service and Windows Credential Manager.

- `trmnl-agent push --merge-file payload.json`
  - Loads JSON, validates schema, wraps under `merge_variables`, and POSTs to TRMNL.

- `trmnl-agent push --stdin`
  - Accepts generated JSON from an agent or script.

- `trmnl-agent preview --merge-file payload.json`
  - Renders a local HTML preview from the Liquid template or a compatible local renderer.

- `trmnl-agent current-screen`
  - Uses optional TRMNL device API credentials to fetch current screen metadata or image.

- `trmnl-agent smoke-test --push --fetch-screen --compare-screen`
  - Runs payload validation, optional live push, optional before/after screen comparison.

### Post-MVP Commands

- `trmnl-agent from-command -- <command>`
- `trmnl-agent from-file --watch status.json`
- `trmnl-agent rate-limit status`
- `trmnl-agent template check`
- `trmnl-agent recipe export`

## Codex Plugin Plan

Build a Codex plugin that contains skills, not heavy code.

Skills:

- `publish-status`
  - Summarizes the current Codex task into the agent-status schema.
  - Calls `trmnl-agent push --stdin` only after checking that secrets are not present.

- `setup`
  - Guides the user through installing the CLI, creating a TRMNL Private Plugin, and storing the webhook.

- `smoke-test`
  - Runs the CLI smoke test and summarizes results.

Plugin manifest:

- `.codex-plugin/plugin.json`
- Include name, version, description, author, repository, license, keywords, skills path, interface metadata, and conservative default prompts.

Marketplace:

- `.agents/plugins/marketplace.json`
- Point to `./plugins/trmnl-agent-bridge`.
- Set category to `Productivity`.
- Set install policy to available.
- Keep authentication as on-install or first-use depending on current Codex validation behavior.

Validation:

- Use Codex local marketplace add flow.
- Verify the plugin appears after restart.
- Verify skill invocation loads the right instructions.
- Verify it can generate a safe payload and call a dry-run CLI command.

## Claude Code Plugin Plan

Build a Claude plugin with the same skill set.

Skills:

- `publish-status`
- `setup`
- `smoke-test`

Plugin manifest:

- `plugins/claude/trmnl-agent-bridge/.claude-plugin/plugin.json`
- Include stable `name`, `description`, `version`, `author`, `homepage`, `repository`, and `license`.

Marketplace:

- `.claude-plugin/marketplace.json`
- Marketplace name: `trmnl-agent-bridge`
- Plugin source: `./plugins/claude/trmnl-agent-bridge`

Validation:

```bash
claude plugin validate .
claude plugin marketplace add ./path/to/repo
claude plugin install trmnl-agent-bridge@trmnl-agent-bridge
```

Then verify:

```text
/trmnl-agent-bridge:setup
/trmnl-agent-bridge:publish-status
```

Do not enable automatic Claude hooks in MVP. A hook that pushes status on `Stop` or `Notification` is useful later, but it should be opt-in because automatic pushes can surprise users and leak context if badly configured.

## TRMNL Plugin And Template Plan

MVP:

- Keep TRMNL as a Private Plugin webhook target.
- Template reads only the public schema fields.
- Template must be legible on 800x480.
- Keep the screen calm: one headline, one detail line, one next-action line, up to four signals.

Post-MVP:

- Add a `recipe/` export package if TRMNL Recipe submission is the preferred public distribution path.
- Add alternative templates:
  - compact task status
  - CI status
  - homelab status
  - multi-agent queue

Do not build a hosted Third Party Plugin until there is clear demand. That path adds OAuth, hosting, per-user state, server operations, and privacy review.

## Implementation Phases

### Phase 0: Rename And Positioning

Status: complete locally on 2026-05-21.

Deliverables:

- Rename repo/package references from `trmnl-codex-bridge` to `trmnl-agent-bridge`.
- Update README headline and examples to mention Codex and Claude equally.
- Preserve `trmnl-codex` only as an optional alias or migration note.

Exit criteria:

- No public-facing file presents the project as Codex-only.
- README explains the three meanings of "plugin": TRMNL display plugin, Codex plugin, Claude plugin.

Implemented:

- Renamed the staging repo directory to the public project name.
- Renamed the Python package to `trmnl_agent_bridge` and the public package to `trmnl-agent-bridge`.
- Updated README, setup docs, security docs, examples, and pyproject metadata to present Codex and Claude Code equally.
- Preserved `trmnl-codex` as a compatibility script alias only.

### Phase 1: Core CLI MVP

Status: implemented and dry-run verified on 2026-05-21; live push remains pending a test Private Plugin webhook.

Deliverables:

- Implement payload load/validate/normalize.
- Implement webhook push using `merge_variables`.
- Implement env var and macOS Keychain credential lookup.
- Implement redacted `status`.
- Add schema and tests.

Exit criteria:

- `trmnl-agent push --merge-file examples/sample-payload.json --dry-run` passes.
- Live push works with a test Private Plugin webhook.
- Unit tests cover payload schema, credential source selection, redaction, and POST body generation.

Implemented:

- Added `src/trmnl_agent_bridge/cli.py`, `credentials.py`, `payloads.py`, and `trmnl.py`.
- Added `schemas/agent-status.v1.schema.json`.
- Implemented payload loading from file, inline JSON, or stdin; validation and normalization; `merge_variables` webhook body generation; size enforcement; environment and macOS Keychain credential lookup; redacted `status`; `setup`; `keychain-set`; dry-run and live `push`; local push-rate limiting.
- Added synthetic Codex and Claude sample payloads.
- Added stdlib `unittest` coverage for payload validation, redaction, credential source precedence, dry-run push, preview, smoke-test dry mode, and current-screen response sanitization.

### Phase 2: Template, Preview, And Smoke Test

Status: implemented and dry-run verified on 2026-05-21; live current-screen comparison remains pending TRMNL credentials and a live push.

Deliverables:

- Rename template to `agent-status.liquid.html`.
- Add local preview output.
- Add current-screen fetch behind optional device API credentials.
- Add smoke test with before/after screen hash comparison.

Exit criteria:

- Local preview renders from sample payload.
- Smoke test can run in dry mode without credentials.
- Live smoke test can verify a screen update when credentials are provided.

Implemented:

- Renamed the Liquid template to `templates/agent-status.liquid.html`.
- Added local 800x480 preview rendering via `trmnl-agent preview`.
- Added optional `trmnl-agent current-screen` fetch using TRMNL device API credentials, with image URL redaction and opt-in image download for hashing.
- Added `trmnl-agent smoke-test` with dry mode, optional live push, optional current-screen fetch, and optional before/after image-hash comparison.

### Phase 3: Codex Plugin Bundle

Status: implemented and locally discovered on 2026-05-21.

Deliverables:

- Add Codex plugin manifest.
- Add Codex skills.
- Add Codex marketplace metadata.
- Add local validation steps to release script.

Exit criteria:

- Codex can discover the marketplace from the local repo.
- Plugin appears in Codex install surface.
- `publish-status` skill can generate a schema-valid payload and invoke CLI dry run.

Implemented:

- Added the Codex plugin bundle at `plugins/trmnl-agent-bridge`.
- Added `.codex-plugin/plugin.json` with public metadata and the `./skills/` path.
- Added `publish-status`, `setup`, and `smoke-test` Codex skills.
- Added repo-local marketplace metadata at `.agents/plugins/marketplace.json`.
- Added `docs/codex-plugin.md` and `scripts/validate-release.sh`.
- Added manifest and marketplace tests in `tests/test_plugin_manifests.py`.
- Verified local Codex marketplace discovery in an isolated temporary `CODEX_HOME`; `codex plugin marketplace add` returned `Added marketplace trmnl-agent-bridge`.

### Phase 4: Claude Code Plugin Bundle

Status: implemented, validated, and installed from the local repo in an isolated temporary Claude home on 2026-05-21.

Deliverables:

- Add Claude plugin manifest.
- Add Claude skills.
- Add Claude marketplace file.
- Add validation script for `claude plugin validate`.

Exit criteria:

- Claude validates marketplace and plugin directory.
- Claude installs the plugin from the local repo.
- Namespaced skills work.

Implemented:

- Added the Claude Code plugin bundle at `plugins/claude/trmnl-agent-bridge`.
- Added `.claude-plugin/plugin.json` with public metadata and the `./skills/` path.
- Added `publish-status`, `setup`, and `smoke-test` Claude skills.
- Added the Claude marketplace manifest at `.claude-plugin/marketplace.json`.
- Added `docs/claude-plugin.md`.
- Updated `scripts/validate-release.sh` to validate Claude manifests and run `claude plugin validate` when Claude is installed.
- Expanded `tests/test_plugin_manifests.py` to cover Claude plugin and marketplace structure.
- Verified `claude plugin validate .` and `claude plugin validate ./plugins/claude/trmnl-agent-bridge`.
- Verified local marketplace registration and plugin install in an isolated temporary `HOME`; `claude plugin install trmnl-agent-bridge@trmnl-agent-bridge --scope local` returned successfully.

### Phase 5: Documentation And Examples

Status: implemented and validated on 2026-05-21.

Deliverables:

- Rewrite README as launch-ready.
- Add `docs/codex-plugin.md`.
- Add `docs/claude-plugin.md`.
- Add `docs/payload-contract.md`.
- Add `docs/release-process.md`.
- Add screenshots or rendered previews only if they contain synthetic data.

Exit criteria:

- A fresh TRMNL user can follow the docs without private context.
- A Codex user can install and dry-run the plugin.
- A Claude user can install and dry-run the plugin.

Implemented:

- Rewrote `README.md` as the launch-oriented first-time flow covering install, dry-run, preview, TRMNL setup, Codex, Claude Code, payload contract, validation, security, layout, roadmap, and non-goals.
- Rewrote `docs/private-plugin-setup.md`, `docs/codex-plugin.md`, and `docs/claude-plugin.md` around concrete fresh-user setup and validation flows.
- Added `docs/payload-contract.md` with required fields, optional fields, state guidance, examples, and validation commands.
- Added `docs/release-process.md` with pre-release checks, live synthetic TRMNL gate, public launch checklist, and remaining blockers.
- Added `tests/test_docs.py` to ensure Phase 5 docs exist, README links core docs, public docs do not reference private workspace names/paths, and stale scaffold language stays out.
- Updated `scripts/validate-release.sh` to require the new docs.
- Kept screenshots/rendered preview assets out of the repo because no synthetic rendered device image has been generated and reviewed yet.

### Phase 6: Security And Release Hardening

Status: implemented locally on 2026-05-21; GitHub-hosted CI still needs to run after the public repo is pushed.

Deliverables:

- Add `scripts/secret-scan.sh`.
- Add GitHub Actions CI for tests, lint, JSON validation, and secret scanning.
- Add `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, and issue templates.
- Add `SECURITY.md` reporting guidance.

Exit criteria:

- CI passes on a clean checkout.
- Secret scan reports no credentials.
- Public docs warn users not to push private payloads or screenshots.

Implemented:

- Added `scripts/secret-scan.sh` and wired it into `scripts/validate-release.sh`.
- Added `.github/workflows/ci.yml` to run release validation and secret scanning on pushes and pull requests.
- Added `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, GitHub issue templates, and issue-template config with private security advisory routing.
- Expanded `SECURITY.md` with reporting guidance, supported-version status, and project security model.
- Rewrote `docs/security.md` with credential handling, repository hygiene, screenshot policy, and scan commands.
- Added `tests/test_release_hardening.py` to require the hardening files and CI wiring.
- Verified `./scripts/secret-scan.sh`, `./scripts/validate-release.sh`, and 26 stdlib tests locally.
- GitHub-hosted CI has not run yet because the public repository has not been pushed.

### Phase 7: Public GitHub Launch

Status: complete for `v0.1.0`; public repo, hosted validation, live synthetic TRMNL gate, tag, and GitHub release completed on 2026-05-21.

Deliverables:

- Create public GitHub repository.
- Push initial main branch.
- Add GitHub topics: `trmnl`, `codex`, `claude-code`, `agent-skills`, `private-plugin`, `e-ink`, `webhooks`.
- Create `v0.1.0` release with release notes.
- Publish installation instructions for CLI, Codex, Claude, and TRMNL Private Plugin setup.

Exit criteria:

- Repo is public.
- Release page is accurate.
- A user can install from GitHub and push a synthetic payload.

Implemented:

- Created the public repository at `https://github.com/jrausercisco/trmnl-agent-bridge`.
- Pushed the initial `main` branch.
- Added GitHub topics: `trmnl`, `codex`, `claude-code`, `agent-skills`, `private-plugin`, `e-ink`, and `webhooks`.
- Confirmed GitHub Actions CI passed on the hosted clean checkout.
- Verified GitHub-hosted Codex marketplace add from an isolated temporary `CODEX_HOME`.
- Verified GitHub-hosted Claude marketplace add and local plugin install from an isolated temporary `HOME`.
- Added `docs/release-notes-v0.1.0.md`.
- Stored the TRMNL Private Plugin webhook in macOS Keychain outside the repo.
- Ran `trmnl-agent push --merge-file examples/sample-payload.json`; the synthetic push returned HTTP 200.
- Ran `trmnl-agent smoke-test --push --fetch-screen --compare-screen --wait-seconds 30`; current-screen fetch succeeded and the screen image hash changed.
- Bumped the package and user agent version to `0.1.0`.
- Created and pushed the annotated `v0.1.0` tag.
- Published the GitHub release at `https://github.com/jrausercisco/trmnl-agent-bridge/releases/tag/v0.1.0`.

### Phase 8: Community Distribution

Deliverables:

- Post in TRMNL community channels with a concise demo and safety posture.
- Open an issue or discussion in `usetrmnl/plugins` asking whether a Recipe/template pointer is welcome.
- Share in Codex and Claude Code communities after installation flows are verified.
- Ask early users for payload/template examples, not private screenshots.

Exit criteria:

- At least one external user can install and run the bridge.
- Installation friction is captured as GitHub issues.

### Phase 9: Post-Launch Roadmap

Candidates:

- PyPI release.
- Homebrew formula.
- Windows Credential Manager and Linux Secret Service support.
- GitHub Action example.
- Built-in template gallery.
- Optional `Stop`/`Notification` hooks for Claude and Codex.
- Optional TRMNL Recipe submission.
- Optional hosted Third Party Plugin only if demand justifies it.

## Test Plan

Core tests:

- JSON schema accepts valid sample payloads.
- JSON schema rejects unknown unsafe shapes when strict mode is enabled.
- Credential resolution prefers CLI argument, then environment, then system credential store.
- Redaction never prints full webhook URLs, tokens, or device IDs.
- Webhook POST body wraps payload under `merge_variables`.
- Payload byte-size warning triggers before push.
- Rate-limit logic avoids unnecessary repeat pushes when `--changed-only` is enabled.

Plugin tests:

- Codex manifest is valid JSON and references existing paths.
- Claude manifest is valid JSON and references existing paths.
- Marketplace files point to self-contained plugin directories.
- Skill frontmatter parses.
- Shared skill text is synchronized between Codex and Claude variants.

Integration tests:

- Dry-run push from sample payload.
- Dry-run push from stdin.
- Optional live push using a test webhook.
- Optional current-screen fetch using device API credentials.
- Optional before/after screen comparison with synthetic payload.

## Security Plan

Security posture:

- No hosted service.
- No telemetry.
- No credentials in config files by default.
- No private payloads in examples.
- No automatic pushes in MVP hooks.
- No raw prompt, transcript, email, calendar, customer, or private note bodies.

Required checks before public push:

```bash
git status --short
./scripts/validate-release.sh
./scripts/secret-scan.sh
```

Use generated screenshots only with synthetic data.

## Release Checklist

- [x] Repo renamed or public naming finalized.
- [x] README explains Codex and Claude support equally.
- [x] CLI MVP implemented and tested.
- [x] Launch-ready documentation flow added.
- [x] TRMNL Private Plugin setup tested with synthetic payload.
- [x] Codex plugin validated locally.
- [x] Claude plugin validated locally.
- [x] Secret scan passed locally.
- [x] CI passed on GitHub.
- [x] Release notes drafted.
- [x] `v0.1.0` tag created.
- [x] Public repo shared.
- [ ] Community feedback issue opened.

## Open Decisions

- Whether to publish to PyPI at `v0.1.0` or wait for `v0.2.0`.
- Whether to include optional hooks in the first release as disabled examples.
- Whether to submit a TRMNL Recipe immediately after `v0.1.0` or wait for user feedback.

## Recommended Next Step

Proceed to Phase 8 community distribution: share the release in TRMNL/Codex/Claude channels, ask for feedback on install friction, and capture any issues in GitHub.
