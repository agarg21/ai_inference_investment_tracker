from __future__ import annotations

import pandas as pd

from ai_power_validation.strategy import build_strategy_windows


def test_strategy_windows_dedupes_same_issuer_day_to_highest_priority_signal():
    events = pd.DataFrame(
        [
            {
                "event_id": "evt_low",
                "issuer": "AEP",
                "trade_date": "2026-02-13",
                "signal_variant": "company_load_forecast",
                "directional_label": "positive",
                "source_confidence": 2,
                "analyst_confidence": 2,
                "mw_value": None,
                "contract_term_years": None,
                "take_or_pay_pct": None,
                "tariff_type": None,
                "cost_recovery": None,
                "capex_mention": None,
            },
            {
                "event_id": "evt_high",
                "issuer": "AEP",
                "trade_date": "2026-02-13",
                "signal_variant": "contracted_load_backlog",
                "directional_label": "positive",
                "source_confidence": 3,
                "analyst_confidence": 3,
                "mw_value": 56_000,
                "contract_term_years": None,
                "take_or_pay_pct": None,
                "tariff_type": None,
                "cost_recovery": None,
                "capex_mention": "$72B capital plan",
            },
        ]
    )
    windows = pd.DataFrame(
        [
            {
                "event_id": "evt_low",
                "ticker": "AEP",
                "horizon": 20,
                "window_end_date": "2026-03-13",
                "raw_return": 0.04,
                "benchmark_xlu_return": 0.01,
                "benchmark_spy_return": 0.02,
                "abnormal_vs_xlu": 0.03,
                "abnormal_vs_spy": 0.02,
            },
            {
                "event_id": "evt_high",
                "ticker": "AEP",
                "horizon": 20,
                "window_end_date": "2026-03-13",
                "raw_return": 0.04,
                "benchmark_xlu_return": 0.01,
                "benchmark_spy_return": 0.02,
                "abnormal_vs_xlu": 0.03,
                "abnormal_vs_spy": 0.02,
            },
        ]
    )

    merged = build_strategy_windows(events, windows)

    assert len(merged) == 1
    assert merged.iloc[0]["event_id"] == "evt_high"
