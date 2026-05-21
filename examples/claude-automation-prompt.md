# Claude Code Automation Prompt Example

Summarize the current Claude Code task into the `agent-status.v1` payload shape and dry-run it:

```bash
trmnl-agent push --stdin --dry-run
```

Use only compact status fields. Do not include prompts, transcripts, customer data, local file bodies, API tokens, webhook URLs, or raw logs.
