from __future__ import annotations

import json

from ai_inference_tracker.inference_tracker import build_inference_tracker


def test_build_inference_tracker_writes_html_and_markdown(settings):
    research_path = settings.data_dir / "inference_thesis_watchlist.json"
    research_path.write_text(
        json.dumps(
            {
                "title": "Inference Tracker",
                "updated_on": "2026-03-29",
                "stance": "Bullish",
                "summary": "Testing tracker generation.",
                "sources": [{"label": "Example", "url": "https://example.com"}],
                "areas": [
                    {
                        "rank": 1,
                        "name": "Power",
                        "bucket": "core",
                        "why_now": "Power matters.",
                        "public_names": ["VRT"],
                        "what_confirms": "Orders stay strong.",
                        "main_risk": "Demand fades.",
                        "research_questions": ["Is backlog rising?"],
                        "sources": [{"label": "Example", "url": "https://example.com"}]
                    }
                ],
                "shortlist": [
                    {
                        "priority": 1,
                        "ticker": "VRT",
                        "company": "Vertiv",
                        "bucket": "core",
                        "area": "Power",
                        "confidence": "high",
                        "thesis": "Power density rises.",
                        "watch_for": "Backlog.",
                        "key_risk": "Demand fades."
                    }
                ],
                "predictions": [
                    {
                        "title": "Power wins",
                        "target_date": "2026-12-31",
                        "status": "open",
                        "statement": "Power remains a bottleneck.",
                        "evidence_to_watch": "Orders and margins.",
                        "falsifier": "Orders weaken."
                    }
                ],
                "history": [
                    {
                        "date": "2026-03-29",
                        "title": "Initial thesis",
                        "summary": "We started the tracker around infrastructure bottlenecks.",
                        "changes": ["Promoted power as the first area to watch."]
                    }
                ]
            }
        )
    )

    html_path, md_path = build_inference_tracker(settings, research_path)

    assert html_path.exists()
    assert md_path.exists()
    assert (settings.root_dir / "site" / "index.html").exists()
    assert (settings.root_dir / "site" / "tracker.md").exists()
    assert "Inference Tracker" in html_path.read_text()
    assert "Dashboard Snapshot" in html_path.read_text()
    assert "Research History" in html_path.read_text()
    assert "Power wins" in md_path.read_text()
    assert "Initial thesis" in md_path.read_text()
