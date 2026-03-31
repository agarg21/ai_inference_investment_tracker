from __future__ import annotations

import json
import shutil
from collections import Counter
from html import escape
from pathlib import Path

from ai_inference_tracker.config import Settings

BASE_CSS = """
:root {
  --bg: #050816;
  --bg-soft: #0b1020;
  --panel: rgba(16, 24, 49, 0.88);
  --panel-strong: rgba(13, 20, 41, 0.96);
  --panel-soft: rgba(255, 255, 255, 0.04);
  --ink: #eef4ff;
  --ink-soft: #b7c3df;
  --ink-faint: #8a96b6;
  --line: rgba(180, 204, 255, 0.14);
  --accent: #6ee7ff;
  --accent-2: #7c9cff;
  --accent-3: #4ade80;
  --warn: #f59e0b;
  --danger: #fb7185;
  --shadow: 0 24px 70px rgba(0, 0, 0, 0.45);
  --radius: 24px;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  color: var(--ink);
  background:
    radial-gradient(circle at top left, rgba(124, 156, 255, 0.18), transparent 28%),
    radial-gradient(circle at top right, rgba(110, 231, 255, 0.12), transparent 24%),
    linear-gradient(180deg, #08101f 0%, var(--bg) 55%, #040611 100%);
  min-height: 100vh;
}
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
.shell {
  width: min(1240px, calc(100vw - 32px));
  margin: 0 auto;
  padding: 24px 0 64px;
}
.topbar {
  position: sticky;
  top: 14px;
  z-index: 20;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 22px;
  padding: 14px 18px;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: rgba(8, 14, 28, 0.82);
  backdrop-filter: blur(18px);
  box-shadow: var(--shadow);
}
.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--ink);
  font-weight: 700;
  letter-spacing: 0.02em;
}
.brand-mark {
  width: 12px;
  height: 12px;
  border-radius: 999px;
  background: linear-gradient(135deg, var(--accent), var(--accent-2));
  box-shadow: 0 0 18px rgba(110, 231, 255, 0.55);
}
.tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.tab {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 40px;
  padding: 0 16px;
  border-radius: 999px;
  color: var(--ink-soft);
  border: 1px solid transparent;
  background: rgba(255, 255, 255, 0.04);
  font-weight: 600;
}
.tab.active {
  color: #07101e;
  background: linear-gradient(135deg, var(--accent), #d0f6ff);
  box-shadow: 0 14px 30px rgba(110, 231, 255, 0.25);
}
.hero {
  display: grid;
  gap: 22px;
  grid-template-columns: minmax(0, 1.4fr) minmax(320px, 0.9fr);
  padding: 34px;
  border-radius: 30px;
  border: 1px solid var(--line);
  background:
    linear-gradient(135deg, rgba(14, 25, 53, 0.96), rgba(8, 13, 28, 0.98)),
    linear-gradient(135deg, rgba(110, 231, 255, 0.12), rgba(124, 156, 255, 0.08));
  box-shadow: var(--shadow);
}
.hero-copy h1 {
  margin: 10px 0 12px;
  font-size: clamp(2.2rem, 4vw, 4rem);
  line-height: 1.02;
  letter-spacing: -0.04em;
}
.hero-copy p {
  margin: 0 0 12px;
  max-width: 70ch;
  color: var(--ink-soft);
  line-height: 1.65;
}
.eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 0.74rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--accent);
}
.hero-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 16px;
}
.pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.06);
  color: var(--ink-soft);
  border: 1px solid var(--line);
  font-size: 0.92rem;
}
.hero-side {
  display: grid;
  gap: 14px;
}
.grid {
  display: grid;
  gap: 18px;
}
.hero-stats {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}
.stats-grid {
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}
.card-grid {
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}
.tracking-grid {
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}
.rank-grid {
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
}
.card,
.stat-card,
.list-card,
.leaderboard-card,
.timeline-card {
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--panel);
  box-shadow: var(--shadow);
}
.card,
.list-card,
.leaderboard-card,
.timeline-card {
  padding: 22px;
}
.stat-card {
  padding: 18px 20px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.06), rgba(255, 255, 255, 0.03));
}
.stat-card .eyebrow {
  color: var(--ink-faint);
}
.stat-card h3,
.card h3,
.leaderboard-card h3,
.timeline-card h3 {
  margin: 8px 0 10px;
  font-size: 1.15rem;
}
.stat-value {
  font-size: clamp(1.4rem, 3vw, 2.2rem);
  font-weight: 800;
  letter-spacing: -0.03em;
}
.muted { color: var(--ink-faint); }
.section {
  margin-top: 28px;
}
.section-head {
  display: flex;
  justify-content: space-between;
  align-items: end;
  gap: 16px;
  margin-bottom: 14px;
}
.section-head h2 {
  margin: 0;
  font-size: clamp(1.4rem, 2vw, 2rem);
}
.section-head p {
  margin: 0;
  color: var(--ink-faint);
}
.source-list,
.bullet-list,
.compact-list {
  margin: 0;
  padding-left: 18px;
  color: var(--ink-soft);
}
.source-list li,
.bullet-list li,
.compact-list li { margin: 8px 0; }
.area-card .meta-row,
.shortlist-card .meta-row,
.provider-card .meta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}
.badge {
  display: inline-flex;
  align-items: center;
  padding: 5px 10px;
  border-radius: 999px;
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.05);
  color: var(--ink-soft);
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.badge.core { color: var(--accent); }
.badge.second_order { color: #cdb8ff; }
.badge.speculative { color: var(--warn); }
.badge.high { color: var(--accent-3); }
.badge.medium { color: #f0abfc; }
.badge.low,
.badge.low-to-medium,
.badge.watchlist { color: var(--warn); }
.badge.avoid,
.badge.danger { color: var(--danger); }
.shortlist-card .ticker-line {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: baseline;
}
.shortlist-card .ticker-line strong {
  font-size: 1.15rem;
}
.shortlist-card p,
.area-card p,
.provider-card p,
.timeline-card p,
.leaderboard-card p {
  color: var(--ink-soft);
}
.matrix {
  display: grid;
  gap: 12px;
}
.matrix-row {
  display: grid;
  grid-template-columns: minmax(150px, 0.9fr) minmax(0, 1.4fr) minmax(120px, 0.8fr);
  gap: 14px;
  padding: 14px 0;
  border-bottom: 1px solid var(--line);
}
.matrix-row:last-child { border-bottom: 0; }
.table-card {
  overflow-x: auto;
}
.comparison-table td strong {
  display: block;
  margin-bottom: 4px;
  color: var(--ink);
}
.comparison-table td span {
  display: block;
  color: var(--ink-faint);
  font-size: 0.88rem;
}
table {
  width: 100%;
  border-collapse: collapse;
  min-width: 720px;
}
th, td {
  padding: 12px 14px;
  border-bottom: 1px solid var(--line);
  text-align: left;
  vertical-align: top;
}
th {
  color: var(--ink-faint);
  font-size: 0.74rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  font-weight: 700;
}
tbody tr:last-child td { border-bottom: 0; }
.leaderboard-list {
  display: grid;
  gap: 10px;
}
.leaderboard-item {
  display: grid;
  grid-template-columns: 36px minmax(0, 1fr) auto;
  gap: 12px;
  align-items: baseline;
  padding: 12px 0;
  border-bottom: 1px solid var(--line);
}
.leaderboard-item:last-child { border-bottom: 0; }
.leaderboard-rank {
  color: var(--ink-faint);
  font-weight: 700;
}
.leaderboard-value {
  text-align: right;
  color: var(--ink);
  font-weight: 700;
}
.leaderboard-sub {
  display: block;
  color: var(--ink-faint);
  font-size: 0.88rem;
  margin-top: 2px;
}
.timeline-card {
  background: linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.025));
}
.callout {
  border-left: 3px solid var(--accent);
  padding-left: 14px;
  margin: 12px 0;
}
.footer-note {
  margin-top: 24px;
  color: var(--ink-faint);
  font-size: 0.92rem;
}
@media (max-width: 960px) {
  .hero { grid-template-columns: 1fr; }
  .hero-stats { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 720px) {
  .shell { width: min(100vw - 20px, 1240px); padding-top: 16px; }
  .topbar { border-radius: 24px; }
  .hero { padding: 24px 20px; }
  .hero-stats,
  .stats-grid,
  .card-grid,
  .rank-grid { grid-template-columns: 1fr; }
  .matrix-row {
    grid-template-columns: 1fr;
    gap: 6px;
  }
}
"""


def _load_json(path: Path) -> dict:
    with path.open() as handle:
        return json.load(handle)


def _load_demand_data(settings: Settings, tracker_data: dict) -> dict:
    demand_path = settings.data_dir / "inference_demand_dashboard.json"
    if demand_path.exists():
        return _load_json(demand_path)

    framework = tracker_data.get("user_demand_framework", {})
    return {
        "title": "Inference Demand Dashboard",
        "updated_on": tracker_data.get("updated_on", ""),
        "standard_metric": {
            "name": "Total processed tokens",
            "definition": "Use input plus output tokens as the primary inference-demand metric when providers disclose them.",
            "why_it_matters": "It maps best to inference workload served."
        },
        "metric_stack": [],
        "kpis": [],
        "provider_snapshots": [],
        "openrouter_live": {},
        "source_library": tracker_data.get("sources", []),
        "segments": framework.get("segments", []),
        "proxies": framework.get("proxies", []),
        "beneficiary_stack": framework.get("beneficiary_stack", []),
        "intro": framework.get("intro", "Inference demand framing.")
    }


def _render_nav(active_tab: str, has_daily_summary: bool) -> str:
    tabs = [
        ("home", "index.html", "Home"),
        ("demand", "user-demand.html", "Inference Demand"),
        ("tracker", "tracker.md", "Tracker Notes"),
    ]
    if has_daily_summary:
        tabs.append(("summary", "daily-summary.md", "Daily Summary"))
    links = []
    for key, href, label in tabs:
        class_name = "tab active" if key == active_tab else "tab"
        links.append(f"<a class='{class_name}' href='{href}'>{escape(label)}</a>")
    return f"""
    <header class="topbar">
      <div class="brand"><span class="brand-mark"></span> AI Inference Investment Tracker</div>
      <nav class="tabs">{''.join(links)}</nav>
    </header>
    """


def _page_shell(title: str, active_tab: str, content: str, *, has_daily_summary: bool) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>{BASE_CSS}</style>
</head>
<body>
  <main class="shell">
    {_render_nav(active_tab, has_daily_summary)}
    {content}
  </main>
</body>
</html>
"""


def _render_links(links: list[dict[str, str]], *, compact: bool = False) -> str:
    if not links:
        return "<p class='muted'>No links yet.</p>"
    class_name = "compact-list" if compact else "source-list"
    items = "".join(
        f"<li><a href='{escape(link['url'])}' target='_blank' rel='noreferrer'>{escape(link['label'])}</a></li>"
        for link in links
    )
    return f"<ul class='{class_name}'>{items}</ul>"


def _render_badge(value: str, extra_class: str = "") -> str:
    class_name = "badge"
    if extra_class:
        class_name += f" {escape(extra_class)}"
    return f"<span class='{class_name}'>{escape(value)}</span>"


def _snapshot_cards(tracker_data: dict, demand_data: dict) -> list[dict[str, str]]:
    areas = tracker_data.get("areas", [])
    shortlist = tracker_data.get("shortlist", [])
    predictions = tracker_data.get("predictions", [])
    demand_kpis = demand_data.get("kpis", [])
    top_area_names = ", ".join(area["name"] for area in areas[:3]) or "No ranked areas yet"
    high_conviction = [item["ticker"] for item in shortlist if item.get("confidence") == "high"]
    lead_names = ", ".join(high_conviction[:5] or [item["ticker"] for item in shortlist[:5]]) or "No shortlist yet"
    bucket_counts = Counter(item.get("bucket", "unknown") for item in shortlist)
    bucket_mix = ", ".join(f"{bucket} {count}" for bucket, count in sorted(bucket_counts.items())) or "No bucket mix yet"
    demand_highlight = demand_kpis[0]["value"] if demand_kpis else "Add demand KPIs"
    demand_note = demand_kpis[0]["label"] if demand_kpis else "Demand tape"
    return [
        {"label": "Current Focus", "value": top_area_names, "note": "Highest-ranked areas right now"},
        {"label": "High-Conviction Names", "value": lead_names, "note": bucket_mix},
        {"label": "Open Predictions", "value": str(sum(1 for item in predictions if item.get("status") == "open")), "note": "Hypotheses still being tested"},
        {"label": demand_note, "value": demand_highlight, "note": "Fresh demand read-through"},
    ]


def _render_stat_cards(items: list[dict[str, str]]) -> str:
    cards = []
    for item in items:
        cards.append(
            f"""
            <section class="stat-card">
              <div class="eyebrow">{escape(item.get("label", ""))}</div>
              <div class="stat-value">{escape(item.get("value", ""))}</div>
              <p class="muted">{escape(item.get("note", ""))}</p>
            </section>
            """
        )
    return "".join(cards)


def _render_area_cards(areas: list[dict]) -> str:
    cards = []
    for area in areas:
        source_links = _render_links(area.get("sources", []), compact=True)
        questions = "".join(f"<li>{escape(item)}</li>" for item in area.get("research_questions", []))
        cards.append(
            f"""
            <section class="card area-card">
              <div class="meta-row">
                {_render_badge(area.get("bucket", "unknown"), area.get("bucket", ""))}
                {_render_badge(f"Rank {int(area.get('rank', 0))}")}
              </div>
              <h3>{escape(area.get("name", ""))}</h3>
              <p>{escape(area.get("why_now", ""))}</p>
              <p><strong>Public names:</strong> {escape(', '.join(area.get('public_names', [])) or 'None yet')}</p>
              <p><strong>What confirms it:</strong> {escape(area.get("what_confirms", ""))}</p>
              <p><strong>Main risk:</strong> {escape(area.get("main_risk", ""))}</p>
              <div class="callout">
                <strong>Research questions</strong>
                <ul class="bullet-list">{questions}</ul>
              </div>
              {source_links}
            </section>
            """
        )
    return "".join(cards)


def _render_shortlist_cards(shortlist: list[dict]) -> str:
    cards = []
    for item in shortlist:
        confidence_class = str(item.get("confidence", "")).lower().replace(" ", "-")
        cards.append(
            f"""
            <section class="card shortlist-card">
              <div class="ticker-line">
                <strong>{escape(item.get("ticker", ""))}</strong>
                {_render_badge(item.get("confidence", ""), confidence_class)}
              </div>
              <p class="muted">{escape(item.get("company", ""))}</p>
              <div class="meta-row">
                {_render_badge(item.get("bucket", ""), item.get("bucket", ""))}
                {_render_badge(item.get("area", ""))}
              </div>
              <p>{escape(item.get("thesis", ""))}</p>
              <p><strong>Watch for:</strong> {escape(item.get("watch_for", ""))}</p>
              <p><strong>Key risk:</strong> {escape(item.get("key_risk", ""))}</p>
            </section>
            """
        )
    return "".join(cards)


def _render_prediction_cards(predictions: list[dict]) -> str:
    cards = []
    for item in predictions:
        status = str(item.get("status", "open")).lower()
        cards.append(
            f"""
            <section class="card">
              <div class="meta-row">
                {_render_badge(item.get("status", "open"), status)}
                {_render_badge(f"Target {item.get('target_date', '')}")}
              </div>
              <h3>{escape(item.get("title", ""))}</h3>
              <p>{escape(item.get("statement", ""))}</p>
              <p><strong>Evidence to watch:</strong> {escape(item.get("evidence_to_watch", ""))}</p>
              <p><strong>How it could fail:</strong> {escape(item.get("falsifier", ""))}</p>
            </section>
            """
        )
    return "".join(cards)


def _render_history_cards(history: list[dict]) -> str:
    if not history:
        return "<section class='timeline-card'><p class='muted'>No research history yet.</p></section>"

    cards = []
    for item in history:
        changes = "".join(f"<li>{escape(change)}</li>" for change in item.get("changes", []))
        cards.append(
            f"""
            <section class="timeline-card">
              <div class="eyebrow">{escape(item.get("date", ""))}</div>
              <h3>{escape(item.get("title", ""))}</h3>
              <p>{escape(item.get("summary", ""))}</p>
              <ul class="bullet-list">{changes}</ul>
            </section>
            """
        )
    return "".join(cards)


def _render_home_page(tracker_data: dict, demand_data: dict, *, has_daily_summary: bool) -> str:
    snapshot_cards = _render_stat_cards(_snapshot_cards(tracker_data, demand_data))
    demand_signal_cards = _render_stat_cards(demand_data.get("kpis", [])[:4])
    content = f"""
    <section class="hero">
      <div class="hero-copy">
        <div class="eyebrow">AI Inference Thesis Tracker</div>
        <h1>{escape(tracker_data.get("title", "AI Inference Tracker"))}</h1>
        <p>{escape(tracker_data.get("summary", ""))}</p>
        <div class="hero-meta">
          <span class="pill">Updated {escape(tracker_data.get("updated_on", ""))}</span>
          <span class="pill">Stance: {escape(tracker_data.get("stance", ""))}</span>
          <a class="pill" href="user-demand.html">Open demand dashboard</a>
        </div>
      </div>
      <div class="hero-side">
        <section class="card">
          <div class="eyebrow">Why this matters</div>
          <h3>Inference is turning into the main compute tape.</h3>
          <p>We track direct tokens where available, then add throughput, message volume, user growth, and seat adoption to understand where inference demand is actually compounding.</p>
          <p class="muted">The design goal is simple: one place to see the best public demand signals, not just thesis notes.</p>
        </section>
        <section class="card">
          <div class="eyebrow">Dashboard Snapshot</div>
          <div class="grid hero-stats">{snapshot_cards}</div>
        </section>
      </div>
    </section>

    <section class="section">
      <div class="section-head">
        <div>
          <h2>Demand Signals</h2>
          <p>Fast read-through metrics that support or challenge the inference-inflection thesis.</p>
        </div>
      </div>
      <div class="grid stats-grid">{demand_signal_cards}</div>
    </section>

    <section class="section">
      <div class="section-head">
        <div>
          <h2>Top-Level Sources</h2>
          <p>Primary references for the core thesis and provider-level demand evidence.</p>
        </div>
      </div>
      <section class="card">{_render_links(tracker_data.get("sources", []))}</section>
    </section>

    <section class="section">
      <div class="section-head">
        <div>
          <h2>Ranked Areas</h2>
          <p>The current market map for where inference demand is most likely to matter first.</p>
        </div>
      </div>
      <div class="grid rank-grid">{_render_area_cards(tracker_data.get("areas", []))}</div>
    </section>

    <section class="section">
      <div class="section-head">
        <div>
          <h2>Shortlist</h2>
          <p>Public names with the clearest relationship to the thesis right now.</p>
        </div>
      </div>
      <div class="grid card-grid">{_render_shortlist_cards(tracker_data.get("shortlist", []))}</div>
    </section>

    <section class="section">
      <div class="section-head">
        <div>
          <h2>Predictions to Track</h2>
          <p>Explicit claims we can revisit instead of hand-waving around the thesis.</p>
        </div>
      </div>
      <div class="grid card-grid">{_render_prediction_cards(tracker_data.get("predictions", []))}</div>
    </section>

    <section class="section">
      <div class="section-head">
        <div>
          <h2>Research History</h2>
          <p>Major changes to the research direction and what caused them.</p>
        </div>
      </div>
      <div class="grid card-grid">{_render_history_cards(tracker_data.get("history", []))}</div>
    </section>

    <p class="footer-note">This homepage is opinionated by design: it should feel closer to a research product than a static memo.</p>
    """
    return _page_shell(tracker_data.get("title", "AI Inference Tracker"), "home", content, has_daily_summary=has_daily_summary)


def _render_metric_stack(items: list[dict]) -> str:
    cards = []
    for item in items:
        cards.append(
            f"""
            <section class="card">
              <div class="meta-row">
                {_render_badge(item.get("importance", ""))}
              </div>
              <h3>{escape(item.get("name", ""))}</h3>
              <p>{escape(item.get("description", ""))}</p>
            </section>
            """
        )
    return "".join(cards)


def _render_tracking_cards(items: list[dict]) -> str:
    cards = []
    for item in items:
        status_class = str(item.get("status", "")).lower().replace(" ", "-")
        cards.append(
            f"""
            <section class="card">
              <div class="meta-row">
                {_render_badge(item.get("cadence", ""))}
                {_render_badge(item.get("status", ""), status_class)}
              </div>
              <h3>{escape(item.get("focus", ""))}</h3>
              <p>{escape(item.get("coverage", ""))}</p>
            </section>
            """
        )
    return "".join(cards)


def _render_comparison_table(rows: list[dict]) -> str:
    body = []
    for row in rows:
        confidence_class = str(row.get("confidence", "")).lower().replace(" ", "-")
        body.append(
            "<tr>"
            f"<td><strong>{escape(row.get('provider', ''))}</strong><span>{escape(row.get('note', ''))}</span></td>"
            f"<td>{escape(row.get('standardized_metric', ''))}</td>"
            f"<td>{escape(row.get('evidence_type', ''))}</td>"
            f"<td>{escape(row.get('weekly_growth', 'n/a'))}</td>"
            f"<td>{escape(row.get('monthly_growth', 'n/a'))}</td>"
            f"<td>{escape(row.get('yearly_growth', 'n/a'))}</td>"
            f"<td>{_render_badge(row.get('confidence', ''), confidence_class)}</td>"
            "</tr>"
        )

    return f"""
    <section class="card table-card comparison-table">
      <table>
        <thead>
          <tr>
            <th>Provider</th>
            <th>Standardized Lens</th>
            <th>Evidence Type</th>
            <th>WoW</th>
            <th>MoM</th>
            <th>YoY</th>
            <th>Confidence</th>
          </tr>
        </thead>
        <tbody>{''.join(body)}</tbody>
      </table>
    </section>
    """


def _render_provider_cards(provider_snapshots: list[dict]) -> str:
    cards = []
    for provider in provider_snapshots:
        rows = "".join(
            "<tr>"
            f"<td>{escape(row.get('date', ''))}</td>"
            f"<td>{escape(row.get('metric', ''))}</td>"
            f"<td>{escape(row.get('value', ''))}</td>"
            f"<td>{escape(row.get('growth', 'n/a'))}</td>"
            "</tr>"
            for row in provider.get("rows", [])
        )
        bullets = "".join(f"<li>{escape(item)}</li>" for item in provider.get("bullets", []))
        estimate = provider.get("estimated_tokens")
        estimate_html = ""
        if estimate:
            estimate_html = f"""
            <div class="callout">
              <strong>Estimated token-equivalent range</strong>
              <p>{escape(estimate.get("method", ""))}</p>
              <p><strong>Low:</strong> {escape(estimate.get("low_daily_tokens", ""))} / day
              <strong>Base:</strong> {escape(estimate.get("base_daily_tokens", ""))} / day
              <strong>High:</strong> {escape(estimate.get("high_daily_tokens", ""))} / day</p>
              <p class="muted">{escape(estimate.get("warning", ""))}</p>
            </div>
            """

        confidence_class = str(provider.get("confidence", "")).lower().replace(" ", "-")
        current_metric = provider.get("current_metric", {})
        cards.append(
            f"""
            <section class="card provider-card">
              <div class="meta-row">
                {_render_badge(provider.get("confidence", ""), confidence_class)}
                {_render_badge(provider.get("measurement", ""))}
              </div>
              <h3>{escape(provider.get("provider", ""))}</h3>
              <p>{escape(provider.get("headline", ""))}</p>
              <div class="callout">
                <strong>{escape(current_metric.get("label", ""))}</strong>
                <p>{escape(current_metric.get("value", ""))} · {escape(current_metric.get("date", ""))}</p>
                <p class="muted">{escape(current_metric.get("growth", ""))}</p>
              </div>
              <section class="table-card">
                <table>
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Metric</th>
                      <th>Value</th>
                      <th>Growth</th>
                    </tr>
                  </thead>
                  <tbody>{rows}</tbody>
                </table>
              </section>
              {estimate_html}
              <ul class="bullet-list">{bullets}</ul>
              {_render_links(provider.get("sources", []), compact=True)}
            </section>
            """
        )
    return "".join(cards)


def _render_leaderboard(title: str, items: list[dict], *, fields: tuple[str, str, str]) -> str:
    primary_field, secondary_field, value_field = fields
    rows = []
    for item in items:
        title_text = item.get(primary_field, "")
        subtitle = item.get(secondary_field, "")
        value = item.get(value_field, "")
        rank = item.get("rank", "")
        rows.append(
            f"""
            <div class="leaderboard-item">
              <div class="leaderboard-rank">{escape(str(rank))}.</div>
              <div>
                <strong>{escape(title_text)}</strong>
                <span class="leaderboard-sub">{escape(subtitle)}</span>
              </div>
              <div class="leaderboard-value">{escape(value)}</div>
            </div>
            """
        )
    return f"""
    <section class="leaderboard-card">
      <h3>{escape(title)}</h3>
      <div class="leaderboard-list">{''.join(rows)}</div>
    </section>
    """


def _render_segments_table(segments: list[dict]) -> str:
    rows = "".join(
        "<tr>"
        f"<td>{escape(item.get('segment', ''))}</td>"
        f"<td>{escape(item.get('today_estimate', ''))}</td>"
        f"<td>{escape(item.get('two_year_view', ''))}</td>"
        f"<td>{escape(item.get('notes', ''))}</td>"
        "</tr>"
        for item in segments
    )
    return f"""
    <section class="card table-card">
      <table>
        <thead>
          <tr>
            <th>Segment</th>
            <th>Today</th>
            <th>2-Year View</th>
            <th>Notes</th>
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>
    </section>
    """


def _render_user_demand_page(tracker_data: dict, demand_data: dict, *, has_daily_summary: bool) -> tuple[str, str]:
    framework = tracker_data.get("user_demand_framework", {})
    segments = demand_data.get("segments", []) or framework.get("segments", [])
    proxies = demand_data.get("proxies", []) or framework.get("proxies", [])
    beneficiaries = demand_data.get("beneficiary_stack", []) or framework.get("beneficiary_stack", [])
    intro = demand_data.get("intro") or framework.get("intro") or "Inference demand measurement framework."
    standard = demand_data.get("standard_metric", {})
    openrouter_live = demand_data.get("openrouter_live", {})

    kpi_cards = _render_stat_cards(demand_data.get("kpis", []))
    metric_stack = _render_metric_stack(demand_data.get("metric_stack", []))
    tracking_cards = _render_tracking_cards(demand_data.get("tracking_plan", []))
    comparison_table = _render_comparison_table(demand_data.get("comparison_rows", []))
    provider_cards = _render_provider_cards(demand_data.get("provider_snapshots", []))
    top_models = _render_leaderboard(
        "OpenRouter Top Models",
        openrouter_live.get("top_models", []),
        fields=("model", "provider", "tokens"),
    )
    author_share = _render_leaderboard(
        "Author Share",
        openrouter_live.get("author_share", []),
        fields=("author", "share", "tokens"),
    )
    top_apps = _render_leaderboard(
        "Top Apps",
        openrouter_live.get("top_apps", []),
        fields=("app", "tokens", "tokens"),
    )
    proxy_list = "".join(
        f"<li><strong>{escape(item.get('name', ''))}:</strong> {escape(item.get('why_it_matters', ''))}</li>"
        for item in proxies
    )
    beneficiary_list = "".join(
        f"<li><strong>{escape(item.get('layer', ''))}:</strong> {escape(item.get('beneficiaries', ''))} — {escape(item.get('logic', ''))}</li>"
        for item in beneficiaries
    )

    html = f"""
    <section class="hero">
      <div class="hero-copy">
        <div class="eyebrow">Inference Demand Dashboard</div>
        <h1>{escape(demand_data.get("title", "Inference Demand Dashboard"))}</h1>
        <p>{escape(intro)}</p>
        <div class="hero-meta">
          <span class="pill">Updated {escape(demand_data.get("updated_on", tracker_data.get("updated_on", "")))}</span>
          <span class="pill">{escape(standard.get("name", ""))}</span>
        </div>
      </div>
      <section class="card">
        <div class="eyebrow">Metric Standard</div>
        <h3>{escape(standard.get("name", ""))}</h3>
        <p>{escape(standard.get("definition", ""))}</p>
        <p class="muted">{escape(standard.get("why_it_matters", ""))}</p>
      </section>
    </section>

    <section class="section">
      <div class="section-head">
        <div>
          <h2>Headline Metrics</h2>
          <p>Best currently available read-throughs for real-world inference demand.</p>
        </div>
      </div>
      <div class="grid stats-grid">{kpi_cards}</div>
    </section>

    <section class="section">
      <div class="section-head">
        <div>
          <h2>Comparable Demand Tape</h2>
          <p>Standardize everything to total processed tokens when possible, then make the estimation quality explicit.</p>
        </div>
      </div>
      {comparison_table}
    </section>

    <section class="section">
      <div class="section-head">
        <div>
          <h2>Tracking Cadence</h2>
          <p>The operating rhythm for turning this from a one-off memo into a durable demand dashboard.</p>
        </div>
      </div>
      <div class="grid tracking-grid">{tracking_cards}</div>
    </section>

    <section class="section">
      <div class="section-head">
        <div>
          <h2>What the Industry Tracks</h2>
          <p>Use the strongest metric available for each provider, then layer weaker proxies only when direct tokens are unavailable.</p>
        </div>
      </div>
      <div class="grid card-grid">{metric_stack}</div>
    </section>

    <section class="section">
      <div class="section-head">
        <div>
          <h2>OpenRouter Live Tape</h2>
          <p>Public marketplace data is the closest thing we have to a transparent weekly demand tape.</p>
        </div>
        <p class="muted">Captured on {escape(openrouter_live.get("captured_on", ""))}</p>
      </div>
      <div class="grid card-grid">
        {top_models}
        {author_share}
        {top_apps}
      </div>
    </section>

    <section class="section">
      <div class="section-head">
        <div>
          <h2>Provider Scorecards</h2>
          <p>Direct tokens where possible, throughput second, and estimated token-equivalents only when we have to.</p>
        </div>
      </div>
      <div class="grid card-grid">{provider_cards}</div>
    </section>

    <section class="section">
      <div class="section-head">
        <div>
          <h2>User-Level Demand Framing</h2>
          <p>How personal, professional, and agentic usage can scale into much larger token budgets per user.</p>
        </div>
      </div>
      {_render_segments_table(segments)}
    </section>

    <section class="section">
      <div class="section-head">
        <div>
          <h2>Practical Proxies</h2>
          <p>Signals to track daily or weekly even when direct provider token data is sparse.</p>
        </div>
      </div>
      <section class="card"><ul class="bullet-list">{proxy_list}</ul></section>
    </section>

    <section class="section">
      <div class="section-head">
        <div>
          <h2>Beneficiary Stack</h2>
          <p>If this demand curve persists, these are the layers most likely to capture value.</p>
        </div>
      </div>
      <section class="card"><ul class="bullet-list">{beneficiary_list}</ul></section>
    </section>

    <section class="section">
      <div class="section-head">
        <div>
          <h2>Source Library</h2>
          <p>Official references and primary documents used in the dashboard.</p>
        </div>
      </div>
      <section class="card">{_render_links(demand_data.get("source_library", []))}</section>
    </section>
    """

    html_page = _page_shell(demand_data.get("title", "Inference Demand Dashboard"), "demand", html, has_daily_summary=has_daily_summary)

    md_lines = [
        f"# {demand_data.get('title', 'Inference Demand Dashboard')}",
        "",
        f"- Updated on: **{demand_data.get('updated_on', tracker_data.get('updated_on', ''))}**",
        f"- Standard metric: **{standard.get('name', '')}**",
        "",
        intro,
        "",
        "## Headline Metrics",
        "",
    ]
    for item in demand_data.get("kpis", []):
        md_lines.append(f"- **{item.get('label', '')}**: {item.get('value', '')} — {item.get('note', '')}")

    md_lines.extend(["", "## Comparable Demand Tape", ""])
    for row in demand_data.get("comparison_rows", []):
        md_lines.extend(
            [
                f"### {row.get('provider', '')}",
                f"- Standardized lens: **{row.get('standardized_metric', '')}**",
                f"- Evidence type: {row.get('evidence_type', '')}",
                f"- WoW: {row.get('weekly_growth', 'n/a')}",
                f"- MoM: {row.get('monthly_growth', 'n/a')}",
                f"- YoY: {row.get('yearly_growth', 'n/a')}",
                f"- Confidence: **{row.get('confidence', '')}**",
                f"- Notes: {row.get('note', '')}",
                "",
            ]
        )

    md_lines.extend(["## Tracking Cadence", ""])
    for item in demand_data.get("tracking_plan", []):
        md_lines.extend(
            [
                f"### {item.get('cadence', '')}",
                f"- Focus: {item.get('focus', '')}",
                f"- Coverage: {item.get('coverage', '')}",
                f"- Status: **{item.get('status', '')}**",
                "",
            ]
        )

    md_lines.extend(["## Metric Stack", ""])
    for item in demand_data.get("metric_stack", []):
        md_lines.extend(
            [
                f"### {item.get('name', '')}",
                f"- Importance: **{item.get('importance', '')}**",
                f"- {item.get('description', '')}",
                "",
            ]
        )

    md_lines.extend(["## Provider Scorecards", ""])
    for provider in demand_data.get("provider_snapshots", []):
        md_lines.extend(
            [
                f"### {provider.get('provider', '')}",
                f"- Confidence: **{provider.get('confidence', '')}**",
                f"- Measurement: {provider.get('measurement', '')}",
                f"- Headline: {provider.get('headline', '')}",
            ]
        )
        current_metric = provider.get("current_metric", {})
        if current_metric:
            md_lines.append(
                f"- Current metric: {current_metric.get('label', '')} = {current_metric.get('value', '')} ({current_metric.get('date', '')}; {current_metric.get('growth', '')})"
            )
        for row in provider.get("rows", []):
            md_lines.append(
                f"- {row.get('date', '')}: {row.get('metric', '')} = {row.get('value', '')} ({row.get('growth', 'n/a')})"
            )
        estimate = provider.get("estimated_tokens")
        if estimate:
            md_lines.append(
                f"- Estimated token-equivalent range: low {estimate.get('low_daily_tokens', '')} / day, base {estimate.get('base_daily_tokens', '')} / day, high {estimate.get('high_daily_tokens', '')} / day"
            )
        for bullet in provider.get("bullets", []):
            md_lines.append(f"- {bullet}")
        md_lines.append("")

    md_lines.extend(["## OpenRouter Live Tape", ""])
    for item in openrouter_live.get("top_models", []):
        md_lines.append(f"- Model #{item.get('rank', '')}: {item.get('model', '')} ({item.get('provider', '')}) — {item.get('tokens', '')}, {item.get('change', '')}")
    md_lines.extend(["", "## User-Level Demand Framing", ""])
    for item in segments:
        md_lines.extend(
            [
                f"### {item.get('segment', '')}",
                f"- Today: {item.get('today_estimate', '')}",
                f"- 2-year view: {item.get('two_year_view', '')}",
                f"- Notes: {item.get('notes', '')}",
                "",
            ]
        )
    md_lines.extend(["## Practical Proxies", ""])
    for item in proxies:
        md_lines.append(f"- **{item.get('name', '')}**: {item.get('why_it_matters', '')}")
    md_lines.extend(["", "## Beneficiary Stack", ""])
    for item in beneficiaries:
        md_lines.append(f"- **{item.get('layer', '')}**: {item.get('beneficiaries', '')} — {item.get('logic', '')}")
    md_lines.extend(["", "## Sources", ""])
    for item in demand_data.get("source_library", []):
        md_lines.append(f"- [{item.get('label', '')}]({item.get('url', '')})")
    md_lines.append("")
    return html_page, "\n".join(md_lines)


def build_inference_tracker(settings: Settings, research_path: Path | None = None) -> tuple[Path, Path]:
    research_path = research_path or settings.data_dir / "inference_thesis_watchlist.json"
    tracker_data = _load_json(research_path)
    demand_data = _load_demand_data(settings, tracker_data)

    html_path = settings.outputs_dir / "inference_tracker.html"
    md_path = settings.outputs_dir / "inference_tracker.md"
    site_dir = settings.root_dir / "site"
    site_dir.mkdir(parents=True, exist_ok=True)

    site_index_path = site_dir / "index.html"
    site_tracker_md_path = site_dir / "tracker.md"
    site_summary_path = site_dir / "daily-summary.md"
    site_user_demand_html_path = site_dir / "user-demand.html"
    site_user_demand_md_path = site_dir / "user-demand.md"
    site_watchlist_path = site_dir / "inference_thesis_watchlist.json"
    site_demand_data_path = site_dir / "inference_demand_dashboard.json"

    daily_summary_path = settings.outputs_dir / "inference_daily_summary.md"
    has_daily_summary = daily_summary_path.exists()

    home_html = _render_home_page(tracker_data, demand_data, has_daily_summary=has_daily_summary)
    html_path.write_text(home_html)
    site_index_path.write_text(home_html)

    snapshot_lines = [
        f"- **{item['label']}**: {item['value']} — {item['note']}"
        for item in _snapshot_cards(tracker_data, demand_data)
    ]
    md_lines = [
        f"# {tracker_data.get('title', 'AI Inference Tracker')}",
        "",
        f"- Updated on: **{tracker_data.get('updated_on', '')}**",
        f"- Stance: **{tracker_data.get('stance', '')}**",
        "",
        "## Summary",
        "",
        tracker_data.get("summary", ""),
        "",
        "## Dashboard Snapshot",
        "",
        *snapshot_lines,
        "",
        "## Ranked Areas",
        "",
    ]
    for area in tracker_data.get("areas", []):
        md_lines.extend(
            [
                f"### {area.get('rank', '')}. {area.get('name', '')}",
                f"- Bucket: **{area.get('bucket', '')}**",
                f"- Why now: {area.get('why_now', '')}",
                f"- Public names: {', '.join(area.get('public_names', [])) or 'None yet'}",
                f"- What confirms it: {area.get('what_confirms', '')}",
                f"- Main risk: {area.get('main_risk', '')}",
                "",
            ]
        )
    md_lines.extend(["## Shortlist", ""])
    for item in tracker_data.get("shortlist", []):
        md_lines.extend(
            [
                f"- `{item.get('priority', '')}` `{item.get('ticker', '')}` `{item.get('company', '')}` [{item.get('bucket', '')}, {item.get('confidence', '')}]",
                f"  Why: {item.get('thesis', '')}",
                f"  Watch: {item.get('watch_for', '')}",
                f"  Risk: {item.get('key_risk', '')}",
            ]
        )
    md_lines.extend(["", "## Predictions", ""])
    for item in tracker_data.get("predictions", []):
        md_lines.extend(
            [
                f"- `{item.get('status', '')}` `{item.get('title', '')}` target `{item.get('target_date', '')}`",
                f"  Statement: {item.get('statement', '')}",
                f"  Evidence to watch: {item.get('evidence_to_watch', '')}",
                f"  Falsifier: {item.get('falsifier', '')}",
            ]
        )
    md_lines.extend(["", "## Research History", ""])
    for item in tracker_data.get("history", []):
        md_lines.extend(
            [
                f"### {item.get('date', '')} - {item.get('title', '')}",
                "",
                item.get("summary", ""),
                "",
            ]
        )
        for change in item.get("changes", []):
            md_lines.append(f"- {change}")
        md_lines.append("")
    markdown = "\n".join(md_lines)
    md_path.write_text(markdown)
    site_tracker_md_path.write_text(markdown)

    demand_html, demand_markdown = _render_user_demand_page(tracker_data, demand_data, has_daily_summary=has_daily_summary)
    site_user_demand_html_path.write_text(demand_html)
    site_user_demand_md_path.write_text(demand_markdown)

    shutil.copy2(research_path, site_watchlist_path)
    demand_source_path = settings.data_dir / "inference_demand_dashboard.json"
    if demand_source_path.exists():
        shutil.copy2(demand_source_path, site_demand_data_path)

    if has_daily_summary:
        shutil.copy2(daily_summary_path, site_summary_path)
    return html_path, md_path
