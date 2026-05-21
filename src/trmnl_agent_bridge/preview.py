"""Local HTML preview renderer for agent-status payloads."""

from __future__ import annotations

import html
import pathlib
from typing import Any


def render_preview(payload: dict[str, Any], destination: pathlib.Path) -> pathlib.Path:
    """Render an 800x480 browser preview from normalized payload fields."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    signals = payload.get("signals") if isinstance(payload.get("signals"), list) else []
    signal_items = "\n".join(
        f'<li>{html.escape(str(signal))}</li>' for signal in signals[:4]
    ) or "<li>No signals yet</li>"
    title = html.escape(str(payload.get("title") or "AGENT NOW"))
    state = html.escape(str(payload.get("state") or "WATCH"))
    headline = html.escape(str(payload.get("headline") or "Waiting for agent status"))
    detail = html.escape(str(payload.get("detail") or "No current status has been pushed."))
    next_action = html.escape(str(payload.get("next") or "Idle"))
    health = html.escape(str(payload.get("health") or "Bridge not checked"))
    updated = html.escape(str(payload.get("updated") or "not updated"))
    source = html.escape(str(payload.get("source") or "agent"))

    document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} TRMNL Preview</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #111;
      --muted: #4c4c4c;
      --line: #111;
      --paper: #f7f7f2;
      --shell: #d8d8d0;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      background: var(--shell);
      color: var(--ink);
      font-family: Arial, Helvetica, sans-serif;
    }}
    .screen {{
      width: 800px;
      height: 480px;
      padding: 26px 30px 22px;
      background: var(--paper);
      border: 1px solid var(--line);
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }}
    .header,
    .footer {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      font-size: 18px;
      line-height: 1.1;
    }}
    .title,
    .state {{
      font-weight: 800;
      letter-spacing: 0;
    }}
    .state {{
      border: 2px solid var(--line);
      padding: 5px 9px;
    }}
    .main {{
      display: flex;
      flex: 1;
      flex-direction: column;
      justify-content: center;
      min-height: 0;
    }}
    h1 {{
      margin: 0 0 12px;
      font-size: 44px;
      line-height: 1.02;
      letter-spacing: 0;
    }}
    .detail {{
      margin: 0 0 22px;
      color: var(--muted);
      font-size: 24px;
      line-height: 1.18;
    }}
    .next {{
      border-top: 2px solid var(--line);
      border-bottom: 2px solid var(--line);
      padding: 12px 0;
      font-size: 22px;
      font-weight: 800;
    }}
    .signals {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px 22px;
      margin: 20px 0 0;
      padding: 0;
      list-style: none;
      font-size: 18px;
      line-height: 1.15;
    }}
    .signals li::before {{
      content: "- ";
    }}
    .footer {{
      border-top: 2px solid var(--line);
      padding-top: 10px;
      font-size: 15px;
    }}
  </style>
</head>
<body>
  <main class="screen" aria-label="TRMNL agent status preview">
    <div class="header">
      <div class="title">{title}</div>
      <div class="state">{state}</div>
    </div>
    <section class="main">
      <h1>{headline}</h1>
      <p class="detail">{detail}</p>
      <div class="next">{next_action}</div>
      <ul class="signals">{signal_items}</ul>
    </section>
    <footer class="footer">
      <span>{source} | {health}</span>
      <span>{updated}</span>
    </footer>
  </main>
</body>
</html>
"""
    destination.write_text(document, encoding="utf-8")
    return destination
