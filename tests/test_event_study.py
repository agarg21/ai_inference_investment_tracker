from __future__ import annotations

import pandas as pd

from ai_power_validation.event_study import build_trade_cards, compute_price_windows


def test_event_study_handles_weekends_and_benchmarks():
    prices = pd.DataFrame(
        {
            "AEP": [100.0, 101.0, 102.0, 104.0],
            "XLU": [50.0, 50.5, 51.0, 51.5],
            "SPY": [500.0, 502.0, 503.0, 506.0],
        },
        index=pd.to_datetime(["2024-07-03", "2024-07-05", "2024-07-08", "2024-07-09"]),
    )
    events = pd.DataFrame(
        [
            {
                "event_id": "evt1",
                "issuer": "AEP",
                "trade_date": "2024-07-05",
                "event_type": "pipeline_mw_increase",
                "directional_label": "positive",
                "source_confidence": 3,
                "analyst_confidence": 2,
            }
        ]
    )
    windows = compute_price_windows(events, prices)
    one_day = windows.loc[windows["horizon"] == 1].iloc[0]
    assert one_day["window_end_date"] == "2024-07-08"
    assert round(one_day["raw_return"], 6) == round(102.0 / 101.0 - 1.0, 6)
    assert "abnormal_vs_xlu" in one_day.index
    assert "abnormal_vs_spy" in one_day.index


def test_trade_cards_filter_to_qualified_buckets():
    events = pd.DataFrame(
        [
            {
                "event_id": f"evt{i}",
                "event_type": "pipeline_mw_increase",
                "directional_label": "positive",
                "source_confidence": 3,
                "analyst_confidence": 2,
            }
            for i in range(8)
        ]
    )
    price_windows = pd.DataFrame(
        [
            {
                "event_id": f"evt{i}",
                "ticker": "AEP",
                "horizon": 20,
                "window_end_date": "2024-08-01",
                "raw_return": 0.08,
                "benchmark_xlu_return": 0.03,
                "benchmark_spy_return": 0.02,
                "abnormal_vs_xlu": 0.05,
                "abnormal_vs_spy": 0.06,
            }
            for i in range(8)
        ]
    )
    trade_cards = build_trade_cards(events, price_windows)
    assert len(trade_cards) == 1
    assert trade_cards.iloc[0]["direction"] == "long"
