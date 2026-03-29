from __future__ import annotations

import json
import shutil
from html import escape
from pathlib import Path

from ai_power_validation.config import Settings


def _load_research_data(path: Path) -> dict:
    with path.open() as handle:
        return json.load(handle)


def _render_links(links: list[dict[str, str]]) -> str:
    if not links:
        return "<p class='muted'>No links yet.</p>"
    items = "".join(
        f"<li><a href='{escape(link['url'])}' target='_blank' rel='noreferrer'>{escape(link['label'])}</a></li>"
        for link in links
    )
    return f"<ul>{items}</ul>"


def _render_area_card(area: dict) -> str:
    public_names = ", ".join(area.get("public_names", [])) or "None yet"
    research_questions = "".join(f"<li>{escape(item)}</li>" for item in area.get("research_questions", []))
    return f"""
    <section class="card">
      <div class="eyebrow">{escape(area["bucket"]).upper()} | Rank {int(area["rank"])}</div>
      <h3>{escape(area["name"])}</h3>
      <p>{escape(area["why_now"])}</p>
      <p><strong>Public names:</strong> {escape(public_names)}</p>
      <p><strong>What would confirm it:</strong> {escape(area["what_confirms"])}</p>
      <p><strong>Main risk:</strong> {escape(area["main_risk"])}</p>
      <div class="subgrid">
        <div>
          <h4>Research Questions</h4>
          <ul>{research_questions}</ul>
        </div>
        <div>
          <h4>Key Sources</h4>
          {_render_links(area.get("sources", []))}
        </div>
      </div>
    </section>
    """


def _render_shortlist_rows(shortlist: list[dict]) -> str:
    rows = []
    for item in shortlist:
        rows.append(
            "<tr>"
            f"<td>{int(item['priority'])}</td>"
            f"<td>{escape(item['ticker'])}</td>"
            f"<td>{escape(item['company'])}</td>"
            f"<td>{escape(item['bucket'])}</td>"
            f"<td>{escape(item['area'])}</td>"
            f"<td>{escape(item['confidence'])}</td>"
            f"<td>{escape(item['thesis'])}</td>"
            f"<td>{escape(item['watch_for'])}</td>"
            f"<td>{escape(item['key_risk'])}</td>"
            "</tr>"
        )
    return "".join(rows)


def _render_predictions(predictions: list[dict]) -> str:
    cards = []
    for item in predictions:
        cards.append(
            f"""
            <section class="card prediction">
              <div class="eyebrow">{escape(item["status"]).upper()} | Target {escape(item["target_date"])}</div>
              <h3>{escape(item["title"])}</h3>
              <p>{escape(item["statement"])}</p>
              <p><strong>Evidence to watch:</strong> {escape(item["evidence_to_watch"])}</p>
              <p><strong>How it could fail:</strong> {escape(item["falsifier"])}</p>
            </section>
            """
        )
    return "".join(cards)


def build_inference_tracker(settings: Settings, research_path: Path | None = None) -> tuple[Path, Path]:
    research_path = research_path or settings.data_dir / "inference_thesis_watchlist.json"
    data = _load_research_data(research_path)

    html_path = settings.outputs_dir / "inference_tracker.html"
    md_path = settings.outputs_dir / "inference_tracker.md"
    site_dir = settings.root_dir / "site"
    site_dir.mkdir(parents=True, exist_ok=True)
    site_index_path = site_dir / "index.html"
    site_summary_path = site_dir / "daily-summary.md"
    site_tracker_md_path = site_dir / "tracker.md"
    site_watchlist_path = site_dir / "inference_thesis_watchlist.json"

    area_cards = "".join(_render_area_card(area) for area in data.get("areas", []))
    shortlist_rows = _render_shortlist_rows(data.get("shortlist", []))
    prediction_cards = _render_predictions(data.get("predictions", []))
    source_links = _render_links(data.get("sources", []))

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI Inference Thesis Tracker</title>
  <style>
    :root {{
      --bg: #f6f1e8;
      --paper: #fffdf9;
      --ink: #1d2228;
      --muted: #5d6570;
      --accent: #1d6b57;
      --accent-soft: #ddeee8;
      --line: #d8d0c3;
      --shadow: 0 18px 40px rgba(29, 34, 40, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Georgia, "Iowan Old Style", serif;
      background: radial-gradient(circle at top left, #fff7df 0, var(--bg) 45%, #efe7da 100%);
      color: var(--ink);
      line-height: 1.55;
    }}
    .page {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 40px 20px 64px;
    }}
    .hero {{
      background: linear-gradient(135deg, rgba(29,107,87,0.95), rgba(24,43,62,0.95));
      color: #f9f6ef;
      padding: 28px;
      border-radius: 24px;
      box-shadow: var(--shadow);
    }}
    .hero h1 {{ margin: 0 0 8px; font-size: 2.4rem; }}
    .hero p {{ margin: 8px 0; max-width: 72ch; }}
    .eyebrow {{
      font-family: "Helvetica Neue", Arial, sans-serif;
      font-size: 0.78rem;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: #d9f3eb;
    }}
    .section-title {{
      margin: 36px 0 14px;
      font-size: 1.65rem;
    }}
    .grid {{
      display: grid;
      gap: 18px;
    }}
    .areas {{
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    }}
    .card {{
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 20px;
      padding: 20px;
      box-shadow: var(--shadow);
    }}
    .card h3 {{ margin-top: 6px; margin-bottom: 10px; }}
    .card h4 {{ margin-bottom: 8px; }}
    .subgrid {{
      display: grid;
      gap: 18px;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    }}
    .muted {{ color: var(--muted); }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: var(--paper);
      border-radius: 20px;
      overflow: hidden;
      box-shadow: var(--shadow);
    }}
    th, td {{
      padding: 12px 10px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
    }}
    th {{
      font-family: "Helvetica Neue", Arial, sans-serif;
      font-size: 0.82rem;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      background: #f0eadf;
    }}
    tr:last-child td {{ border-bottom: 0; }}
    a {{ color: var(--accent); }}
    .prediction {{
      border-left: 6px solid var(--accent);
    }}
    @media (max-width: 720px) {{
      .hero h1 {{ font-size: 1.8rem; }}
      table, thead, tbody, th, td, tr {{ display: block; }}
      thead {{ display: none; }}
      td {{
        padding: 10px 12px;
      }}
    }}
  </style>
</head>
<body>
  <main class="page">
    <section class="hero">
      <div class="eyebrow">AI Inference Thesis Tracker</div>
      <h1>{escape(data["title"])}</h1>
      <p>{escape(data["summary"])}</p>
      <p><strong>Last updated:</strong> {escape(data["updated_on"])}</p>
      <p><strong>Current stance:</strong> {escape(data["stance"])}</p>
    </section>

    <h2 class="section-title">Top-Level Sources</h2>
    <section class="card">{source_links}</section>

    <h2 class="section-title">Ranked Areas</h2>
    <section class="grid areas">{area_cards}</section>

    <h2 class="section-title">Shortlist</h2>
    <table>
      <thead>
        <tr>
          <th>Rank</th>
          <th>Ticker</th>
          <th>Company</th>
          <th>Bucket</th>
          <th>Area</th>
          <th>Confidence</th>
          <th>Why It Matters</th>
          <th>Watch For</th>
          <th>Risk</th>
        </tr>
      </thead>
      <tbody>{shortlist_rows}</tbody>
    </table>

    <h2 class="section-title">Predictions To Track</h2>
    <section class="grid">{prediction_cards}</section>
  </main>
</body>
</html>
"""
    html_path.write_text(html)
    site_index_path.write_text(html)

    md_lines = [
        f"# {data['title']}",
        "",
        f"- Updated on: **{data['updated_on']}**",
        f"- Stance: **{data['stance']}**",
        "",
        "## Summary",
        "",
        data["summary"],
        "",
        "## Ranked Areas",
        "",
    ]
    for area in data.get("areas", []):
        md_lines.extend(
            [
                f"### {area['rank']}. {area['name']}",
                "",
                f"- Bucket: **{area['bucket']}**",
                f"- Why now: {area['why_now']}",
                f"- Public names: {', '.join(area.get('public_names', [])) or 'None yet'}",
                f"- What confirms it: {area['what_confirms']}",
                f"- Main risk: {area['main_risk']}",
                "",
            ]
        )

    md_lines.extend(["## Shortlist", ""])
    for item in data.get("shortlist", []):
        md_lines.extend(
            [
                f"- `{item['priority']}` `{item['ticker']}` `{item['company']}` [{item['bucket']}, {item['confidence']}]",
                f"  Why: {item['thesis']}",
                f"  Watch: {item['watch_for']}",
                f"  Risk: {item['key_risk']}",
            ]
        )

    md_lines.extend(["", "## Predictions", ""])
    for item in data.get("predictions", []):
        md_lines.extend(
            [
                f"- `{item['status']}` `{item['title']}` target `{item['target_date']}`",
                f"  Statement: {item['statement']}",
                f"  Evidence to watch: {item['evidence_to_watch']}",
                f"  Falsifier: {item['falsifier']}",
            ]
        )

    markdown = "\n".join(md_lines) + "\n"
    md_path.write_text(markdown)
    site_tracker_md_path.write_text(markdown)
    shutil.copy2(research_path, site_watchlist_path)

    daily_summary_path = settings.outputs_dir / "inference_daily_summary.md"
    if daily_summary_path.exists():
        shutil.copy2(daily_summary_path, site_summary_path)
    return html_path, md_path
