from __future__ import annotations

import pandas as pd

from ai_power_validation.reporting import build_historical_setup_summary, build_recommendation_book, build_trading_spec


def test_trading_spec_prefers_non_low_variants_and_exports_supporting_files(settings):
    events = pd.DataFrame(
        [
            {
                "event_id": "evt1",
                "trade_date": "2026-01-08",
                "issuer": "AEP",
                "event_type": "pipeline_mw_increase",
                "signal_variant": "company_load_forecast",
                "directional_label": "positive",
                "mw_value": None,
                "contract_term_years": None,
                "take_or_pay_pct": None,
                "tariff_type": None,
                "cost_recovery": None,
                "capex_mention": None,
                "source_confidence": 3,
                "analyst_confidence": 2,
                "evidence_snippet": "Load forecast improved.",
            },
            {
                "event_id": "evt2",
                "trade_date": "2026-02-13",
                "issuer": "AEP",
                "event_type": "pipeline_mw_increase",
                "signal_variant": "company_load_forecast",
                "directional_label": "positive",
                "mw_value": None,
                "contract_term_years": None,
                "take_or_pay_pct": None,
                "tariff_type": None,
                "cost_recovery": None,
                "capex_mention": "$1B capex",
                "source_confidence": 3,
                "analyst_confidence": 2,
                "evidence_snippet": "Another load forecast improvement.",
            },
            {
                "event_id": "evt3",
                "trade_date": "2026-01-08",
                "issuer": "FE",
                "event_type": "pipeline_mw_increase",
                "signal_variant": "regional_grid_readthrough",
                "directional_label": "positive",
                "mw_value": 30000,
                "contract_term_years": None,
                "take_or_pay_pct": None,
                "tariff_type": None,
                "cost_recovery": None,
                "capex_mention": None,
                "source_confidence": 3,
                "analyst_confidence": 2,
                "evidence_snippet": "Regional read-through.",
            },
            {
                "event_id": "evt4",
                "trade_date": "2026-01-09",
                "issuer": "AEP",
                "event_type": "pipeline_mw_increase",
                "signal_variant": "regional_grid_readthrough",
                "directional_label": "positive",
                "mw_value": 30000,
                "contract_term_years": None,
                "take_or_pay_pct": None,
                "tariff_type": None,
                "cost_recovery": None,
                "capex_mention": None,
                "source_confidence": 2,
                "analyst_confidence": 2,
                "evidence_snippet": "Another regional read-through.",
            },
            {
                "event_id": "evt5",
                "trade_date": "2026-01-10",
                "issuer": "PNW",
                "event_type": "tariff_or_special_rate_approval",
                "signal_variant": "proposed_rate_design",
                "directional_label": "positive",
                "mw_value": None,
                "contract_term_years": None,
                "take_or_pay_pct": None,
                "tariff_type": "rate_design_update",
                "cost_recovery": None,
                "capex_mention": None,
                "source_confidence": 2,
                "analyst_confidence": 2,
                "evidence_snippet": "Proposed tariff only.",
            },
        ]
    )
    windows = pd.DataFrame(
        [
            {"event_id": "evt1", "horizon": 20, "abnormal_vs_xlu": 0.01},
            {"event_id": "evt2", "horizon": 20, "abnormal_vs_xlu": 0.02},
            {"event_id": "evt3", "horizon": 20, "abnormal_vs_xlu": 0.03},
            {"event_id": "evt4", "horizon": 20, "abnormal_vs_xlu": 0.01},
            {"event_id": "evt5", "horizon": 20, "abnormal_vs_xlu": -0.02},
        ]
    )

    path = build_trading_spec(settings, events, windows)
    content = path.read_text()

    assert "`company_load_forecast` (`medium` tier)" in content
    assert "`regional_grid_readthrough` (`low` tier)" in content
    assert "`proposed_rate_design` at `+20`" in content
    assert "## Recommendation Book" in content
    assert (settings.outputs_dir / "issuer_signal_summary.csv").exists()
    assert (settings.outputs_dir / "historical_setups.csv").exists()
    assert (settings.outputs_dir / "recommendation_book.csv").exists()


def test_historical_setup_summary_orders_preferred_before_avoid():
    events = pd.DataFrame(
        [
            {
                "event_id": "evt1",
                "trade_date": "2026-01-08",
                "issuer": "AEP",
                "event_type": "pipeline_mw_increase",
                "signal_variant": "company_load_forecast",
                "directional_label": "positive",
                "mw_value": None,
                "contract_term_years": None,
                "take_or_pay_pct": None,
                "tariff_type": None,
                "cost_recovery": None,
                "capex_mention": "$1B capex",
                "source_confidence": 3,
                "analyst_confidence": 2,
                "evidence_snippet": "Preferred setup.",
            },
            {
                "event_id": "evt2",
                "trade_date": "2026-01-09",
                "issuer": "PNW",
                "event_type": "tariff_or_special_rate_approval",
                "signal_variant": "proposed_rate_design",
                "directional_label": "positive",
                "mw_value": None,
                "contract_term_years": None,
                "take_or_pay_pct": None,
                "tariff_type": "rate_design_update",
                "cost_recovery": None,
                "capex_mention": None,
                "source_confidence": 2,
                "analyst_confidence": 2,
                "evidence_snippet": "Avoid setup.",
            },
        ]
    )
    windows = pd.DataFrame(
        [
            {"event_id": "evt1", "horizon": 20, "abnormal_vs_xlu": 0.02},
            {"event_id": "evt2", "horizon": 20, "abnormal_vs_xlu": -0.01},
        ]
    )
    variant_summary = pd.DataFrame(
        [
            {
                "signal_variant": "company_load_forecast",
                "signal_tier": "medium",
                "horizon": 20,
                "sample_count": 2,
                "hit_rate": 0.8,
                "median_abnormal_return": 0.015,
                "mean_abnormal_return": 0.015,
            },
            {
                "signal_variant": "proposed_rate_design",
                "signal_tier": "low",
                "horizon": 20,
                "sample_count": 1,
                "hit_rate": 0.0,
                "median_abnormal_return": -0.01,
                "mean_abnormal_return": -0.01,
            },
        ]
    )

    summary = build_historical_setup_summary(events, windows, variant_summary)
    assert summary.iloc[0]["family_bucket"] == "preferred"
    assert summary.iloc[1]["family_bucket"] == "exploratory"


def test_recommendation_book_ranks_high_confidence_before_avoid():
    events = pd.DataFrame(
        [
            {
                "event_id": "evt1",
                "trade_date": "2026-01-08",
                "issuer": "FE",
                "event_type": "transmission_or_interconnection_approval",
                "signal_variant": "transmission_capex_growth",
                "directional_label": "positive",
            },
            {
                "event_id": "evt2",
                "trade_date": "2026-02-13",
                "issuer": "FE",
                "event_type": "transmission_or_interconnection_approval",
                "signal_variant": "transmission_capex_growth",
                "directional_label": "positive",
            },
            {
                "event_id": "evt3",
                "trade_date": "2026-01-09",
                "issuer": "POR",
                "event_type": "pipeline_mw_increase",
                "signal_variant": "company_load_forecast",
                "directional_label": "positive",
            },
            {
                "event_id": "evt4",
                "trade_date": "2026-02-16",
                "issuer": "POR",
                "event_type": "pipeline_mw_increase",
                "signal_variant": "company_load_forecast",
                "directional_label": "positive",
            },
        ]
    )
    windows = pd.DataFrame(
        [
            {"event_id": "evt1", "ticker": "FE", "horizon": 20, "abnormal_vs_xlu": 0.03},
            {"event_id": "evt2", "ticker": "FE", "horizon": 20, "abnormal_vs_xlu": 0.02},
            {"event_id": "evt3", "ticker": "POR", "horizon": 20, "abnormal_vs_xlu": -0.01},
            {"event_id": "evt4", "ticker": "POR", "horizon": 20, "abnormal_vs_xlu": -0.02},
        ]
    )

    summary = build_recommendation_book(events, windows)
    assert summary.iloc[0]["issuer"] == "FE"
    assert summary.iloc[0]["confidence"] == "high"
    assert summary.iloc[-1]["issuer"] == "POR"
    assert summary.iloc[-1]["confidence"] == "avoid"
