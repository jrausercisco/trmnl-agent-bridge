# TRMNL Private Plugin Setup

Use this guide to connect `trmnl-agent` to a TRMNL Private Plugin webhook.

## Prerequisites

- A TRMNL account with a target device or BYOD setup.
- A local checkout or installed copy of `trmnl-agent-bridge`.
- No private payloads in this repo. Use the synthetic examples first.

## Create The Private Plugin

1. Open the TRMNL web app.
2. Create a Private Plugin.
3. Choose the webhook data retrieval strategy. Do not choose polling, static, plugin merge, or async polling for the first setup.
4. Paste the raw contents of `templates/agent-status.liquid.html` into the markup editor.
5. Save the plugin so TRMNL generates the webhook URL.
6. Assign the plugin to the target device playlist.

TRMNL expects webhook updates under a top-level `merge_variables` object. The CLI creates that wrapper for you.

On macOS, copy the raw markup from the repository checkout with:

```bash
pbcopy < templates/agent-status.liquid.html
```

Avoid copying from a browser-rendered preview of the `.html` file. The editor needs the markup source beginning with `<div class="layout...">`; if it starts with `{{ title ... }}`, the HTML tags were stripped before paste.

## First Webhook Checklist

The first successful setup depends on three separate pieces being correct: the TRMNL plugin strategy, the markup source, and the local webhook credential.

1. In TRMNL, confirm the Private Plugin strategy is `Webhook`.
2. In the markup editor, paste the raw template source from `templates/agent-status.liquid.html`.
3. Save the markup and check the TRMNL preview before sending data.
4. Copy the generated webhook URL from the plugin settings.
5. Store the webhook URL locally with `trmnl-agent keychain-set --account TRMNL_WEBHOOK_URL` or `TRMNL_WEBHOOK_URL`.
6. Send only `examples/sample-payload.json` until the device renders correctly.

The webhook URL is only for data updates. It does not configure the markup template, plugin layout, playlist assignment, or refresh interval.

## Common Setup Pitfalls

If the preview shows plain text instead of a designed layout, the markup editor probably received rendered text instead of raw HTML. Re-copy with:

```bash
pbcopy < templates/agent-status.liquid.html
```

If `trmnl-agent status` says the webhook is missing, store the generated webhook URL again and avoid shell history if your terminal records commands:

```bash
trmnl-agent keychain-set --account TRMNL_WEBHOOK_URL
```

If `trmnl-agent push` succeeds but the screen does not change, verify the plugin is assigned to the target device playlist and allow time for the device to refresh. If you have device API credentials, use the screen comparison smoke test below to confirm whether TRMNL produced a new render.

If the live payload is rejected, dry-run the same merge file first. The bridge validates payload shape and size before posting, but TRMNL still expects the JSON body to be wrapped as `merge_variables`; use `trmnl-agent push` rather than a hand-written curl command for first setup.

Do not paste webhook URLs, response JSON, or device screenshots into public issues unless you have redacted secrets and verified the screenshot contains only synthetic data.

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
