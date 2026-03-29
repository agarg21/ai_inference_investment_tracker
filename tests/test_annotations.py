from __future__ import annotations

import csv

import pandas as pd

from ai_inference_tracker.annotations import normalize_trade_date, persist_events, prepare_event_records
from ai_inference_tracker.db import get_connection


def test_prepare_events_and_round_trip_into_db(settings):
    source_df = pd.DataFrame(
        [
            {
                "id": 1,
                "source_url": "https://example.com/aep-doc",
                "document_date": "2026-01-08",
            }
        ]
    )
    rows = [
        {
            "annotation_id": "1",
            "canonical_event_key": "AEP::tariff::2026-01-08",
            "source_url": "https://example.com/aep-doc",
            "issuer": "AEP",
            "event_type": "tariff_or_special_rate_approval",
            "event_timestamp": "2026-01-08T15:30:00-05:00",
            "trade_date_override": "",
            "region": "PJM",
            "mw_value": "500",
            "contract_term_years": "20",
            "take_or_pay_pct": "90",
            "tariff_type": "large_load_tariff",
            "cost_recovery": "full",
            "capex_mention": "$250M/GW",
            "directional_label": "positive",
            "source_confidence": "3",
            "analyst_confidence": "2",
            "evidence_snippet": "New 20-year tariff with take-or-pay protection.",
            "notes": "Sample note",
        }
    ]
    trading_days = pd.to_datetime(["2026-01-08", "2026-01-09", "2026-01-12"])
    records = prepare_event_records(rows, source_df, trading_days)
    event_df = persist_events(settings, records, source_df)
    assert event_df.iloc[0]["mw_value"] == 500.0
    assert event_df.iloc[0]["take_or_pay_pct"] == 90.0

    with get_connection(settings) as connection:
        db_row = connection.execute("SELECT * FROM events").fetchone()
        assert db_row["tariff_type"] == "large_load_tariff"
        assert db_row["cost_recovery"] == "full"


def test_deduplicates_rows_with_same_canonical_key(settings):
    source_df = pd.DataFrame(
        [
            {"id": 1, "source_url": "https://example.com/doc-1", "document_date": "2026-01-08"},
            {"id": 2, "source_url": "https://example.com/doc-2", "document_date": "2026-01-08"},
        ]
    )
    rows = [
        {
            "annotation_id": "1",
            "canonical_event_key": "FE::pipeline::2026-01-08",
            "source_url": "https://example.com/doc-1",
            "issuer": "FE",
            "event_type": "pipeline_mw_increase",
            "event_timestamp": "2026-01-08T10:00:00-05:00",
            "trade_date_override": "",
            "region": "PJM",
            "mw_value": "1000",
            "contract_term_years": "",
            "take_or_pay_pct": "",
            "tariff_type": "",
            "cost_recovery": "",
            "capex_mention": "",
            "directional_label": "positive",
            "source_confidence": "2",
            "analyst_confidence": "2",
            "evidence_snippet": "Pipeline increased.",
            "notes": "",
        },
        {
            "annotation_id": "2",
            "canonical_event_key": "FE::pipeline::2026-01-08",
            "source_url": "https://example.com/doc-2",
            "issuer": "FE",
            "event_type": "pipeline_mw_increase",
            "event_timestamp": "2026-01-08T10:00:00-05:00",
            "trade_date_override": "",
            "region": "PJM",
            "mw_value": "1000",
            "contract_term_years": "",
            "take_or_pay_pct": "",
            "tariff_type": "",
            "cost_recovery": "",
            "capex_mention": "",
            "directional_label": "positive",
            "source_confidence": "3",
            "analyst_confidence": "2",
            "evidence_snippet": "Same event from deck.",
            "notes": "",
        },
    ]
    trading_days = pd.to_datetime(["2026-01-08", "2026-01-09"])
    records = prepare_event_records(rows, source_df, trading_days)
    persist_events(settings, records, source_df)

    with get_connection(settings) as connection:
        event_count = connection.execute("SELECT COUNT(*) AS count FROM events").fetchone()["count"]
        link_count = connection.execute("SELECT COUNT(*) AS count FROM event_source_links").fetchone()["count"]
    assert event_count == 1
    assert link_count == 2


def test_normalize_trade_date_before_and_after_close():
    trading_days = pd.to_datetime(["2026-01-08", "2026-01-09", "2026-01-12"])
    before_close = normalize_trade_date(
        event_timestamp="2026-01-08T15:59:00-05:00",
        document_date="2026-01-08",
        trade_date_override=None,
        trading_days=trading_days,
    )
    after_close = normalize_trade_date(
        event_timestamp="2026-01-08T16:01:00-05:00",
        document_date="2026-01-08",
        trade_date_override=None,
        trading_days=trading_days,
    )
    assert before_close == "2026-01-08"
    assert after_close == "2026-01-09"
