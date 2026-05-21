"""Local HTML preview renderer for agent-status payloads."""

from __future__ import annotations

import html
import pathlib
from typing import Any


LAYOUT_SIZES = {
    "full": (800, 480),
    "half-horizontal": (800, 240),
    "half-vertical": (400, 480),
    "quadrant": (400, 240),
}


def render_preview(
    payload: dict[str, Any],
    destination: pathlib.Path,
    *,
    layout: str = "full",
) -> pathlib.Path:
    """Render a browser preview from normalized payload fields."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    if layout not in LAYOUT_SIZES:
        choices = ", ".join(sorted(LAYOUT_SIZES))
        raise ValueError(f"layout must be one of: {choices}")

    width, height = LAYOUT_SIZES[layout]
    is_small = layout in {"half-horizontal", "quadrant"}
    is_narrow = layout in {"half-vertical", "quadrant"}
    signals = payload.get("signals") if isinstance(payload.get("signals"), list) else []
    signal_limit = 0 if layout == "quadrant" else 3 if layout == "half-vertical" else 4
    signal_items = "\n".join(
        f'<li>{html.escape(str(signal))}</li>' for signal in signals[:signal_limit]
    ) or ("<li>No signals yet</li>" if signal_limit else "")
    title = html.escape(str(payload.get("title") or "AGENT NOW"))
    state = html.escape(str(payload.get("state") or "WATCH"))
    headline = html.escape(str(payload.get("headline") or "Waiting for agent status"))
    detail = html.escape(str(payload.get("detail") or "No current status has been pushed."))
    next_action = html.escape(str(payload.get("next") or "Idle"))
    health = html.escape(str(payload.get("health") or "Bridge not checked"))
    updated = html.escape(str(payload.get("updated") or "not updated"))
    source = html.escape(str(payload.get("source") or "agent"))
    padding_y = 14 if is_small else 24
    padding_x = 18 if is_narrow else 30
    headline_size = 26 if is_small else 34 if is_narrow else 44
    detail_size = 15 if is_small else 18 if is_narrow else 24
    next_size = 15 if is_small else 18 if is_narrow else 22
    header_size = 15 if is_small else 17 if is_narrow else 18
    footer_size = 12 if is_small else 14 if is_narrow else 15
    signal_columns = 1 if is_narrow else 4 if layout == "half-horizontal" else 2
    show_detail = layout != "quadrant"
    show_signals = signal_limit > 0

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
      width: {width}px;
      height: {height}px;
      padding: {padding_y}px {padding_x}px;
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
      font-size: {header_size}px;
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
      margin: 0 0 {8 if is_small else 12}px;
      font-size: {headline_size}px;
      line-height: 1.02;
      letter-spacing: 0;
    }}
    .detail {{
      margin: 0 0 {10 if is_small else 18}px;
      color: var(--muted);
      font-size: {detail_size}px;
      line-height: 1.18;
    }}
    .next {{
      border-top: 2px solid var(--line);
      border-bottom: 2px solid var(--line);
      padding: {7 if is_small else 12}px 0;
      font-size: {next_size}px;
      font-weight: 800;
    }}
    .signals {{
      display: grid;
      grid-template-columns: repeat({signal_columns}, minmax(0, 1fr));
      gap: 5px 16px;
      margin: {10 if is_small else 18}px 0 0;
      padding: 0;
      list-style: none;
      font-size: {13 if is_small else 16 if is_narrow else 18}px;
      line-height: 1.15;
    }}
    .signals li::before {{
      content: "- ";
    }}
    .footer {{
      border-top: 2px solid var(--line);
      padding-top: {7 if is_small else 10}px;
      font-size: {footer_size}px;
    }}
  </style>
</head>
<body>
  <main class="screen" aria-label="TRMNL {layout} agent status preview">
    <div class="header">
      <div class="title">{title}</div>
      <div class="state">{state}</div>
    </div>
    <section class="main">
      <h1>{headline}</h1>
      {f'<p class="detail">{detail}</p>' if show_detail else ''}
      <div class="next">{next_action}</div>
      {f'<ul class="signals">{signal_items}</ul>' if show_signals else ''}
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
