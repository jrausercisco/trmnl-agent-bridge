# TRMNL Private Plugin Setup

Use this guide to connect `trmnl-agent` to a TRMNL Private Plugin webhook.

## Prerequisites

- A TRMNL account with a target device or BYOD setup.
- A local checkout or installed copy of `trmnl-agent-bridge`.
- No private payloads in this repo. Use the synthetic examples first.

## Create The Private Plugin

1. Open the TRMNL web app.
2. Create a Private Plugin.
3. Choose the webhook data retrieval strategy.
4. Paste the raw contents of `templates/agent-status.liquid.html` into the markup editor.
5. Save the plugin so TRMNL generates the webhook URL.
6. Assign the plugin to the target device playlist.

TRMNL expects webhook updates under a top-level `merge_variables` object. The CLI creates that wrapper for you.

On macOS, copy the raw markup from the repository checkout with:

```bash
pbcopy < templates/agent-status.liquid.html
```

Avoid copying from a browser-rendered preview of the `.html` file. The editor needs the markup source beginning with `<div class="layout...">`; if it starts with `{{ title ... }}`, the HTML tags were stripped before paste.

## Store The Webhook Secret

Use one of these credential sources:

```bash
export TRMNL_WEBHOOK_URL="<private-plugin-webhook-url>"
```

or:

```bash
trmnl-agent keychain-set --account TRMNL_WEBHOOK_URL
```

Do not commit the webhook URL to `.env`, docs, examples, screenshots, issue bodies, or logs.

## Test Locally First

Dry-run the payload:

```bash
trmnl-agent push --merge-file examples/sample-payload.json --dry-run
```

Render a local preview:

```bash
trmnl-agent preview --merge-file examples/sample-payload.json
```

Run the dry smoke test:

```bash
trmnl-agent smoke-test
```

## Push Synthetic Data

After the webhook is stored:

```bash
trmnl-agent push --merge-file examples/sample-payload.json
```

Keep the first live push synthetic. Do not use real prompts, logs, email/calendar content, customer data, local file bodies, or private notes.

## Optional Screen Verification

If you also have TRMNL device API credentials, store them outside the repo:

```bash
trmnl-agent keychain-set --account TRMNL_ACCESS_TOKEN
trmnl-agent keychain-set --account TRMNL_DEVICE_ID
```

Then run:

```bash
trmnl-agent smoke-test --push --fetch-screen --compare-screen --wait-seconds 30
```

Screen image downloads are opt-in and should be treated as private unless they contain only synthetic data.

## Rate And Size Expectations

The CLI enforces a conservative payload limit and local push cap. TRMNL’s documented webhook limits are small by design, so send the current signal, not a dashboard dump.
