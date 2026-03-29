from __future__ import annotations

import pandas as pd

from ai_power_validation.constants import SIGNAL_TIER_BY_VARIANT


def add_event_priority(events_df: pd.DataFrame) -> pd.DataFrame:
    if events_df.empty:
        return events_df.copy()

    prioritized = events_df.copy()
    for column, default in {
        "signal_variant": None,
        "source_confidence": 0,
        "analyst_confidence": 0,
        "mw_value": None,
        "contract_term_years": None,
        "take_or_pay_pct": None,
        "tariff_type": None,
        "cost_recovery": None,
        "capex_mention": None,
    }.items():
        if column not in prioritized.columns:
            prioritized[column] = default
    prioritized["signal_tier"] = prioritized["signal_variant"].map(SIGNAL_TIER_BY_VARIANT).fillna("unknown")
    prioritized["event_priority"] = prioritized["signal_tier"].map({"high": 3, "medium": 2, "low": 0}).fillna(1)
    prioritized["event_priority"] += prioritized["source_confidence"].fillna(0).astype(int)
    prioritized["event_priority"] += prioritized["analyst_confidence"].fillna(0).astype(int)
    prioritized["event_priority"] += prioritized["mw_value"].notna().astype(int)
    prioritized["event_priority"] += (
        prioritized["contract_term_years"].notna() | prioritized["take_or_pay_pct"].notna()
    ).astype(int)
    prioritized["event_priority"] += (
        prioritized["tariff_type"].fillna("").ne("")
        | prioritized["cost_recovery"].fillna("").ne("")
        | prioritized["capex_mention"].fillna("").ne("")
    ).astype(int)
    return prioritized


def build_strategy_windows(events_df: pd.DataFrame, price_windows_df: pd.DataFrame) -> pd.DataFrame:
    if events_df.empty or price_windows_df.empty:
        return pd.DataFrame()

    prioritized = add_event_priority(events_df)
    merged = price_windows_df.merge(prioritized, on="event_id", how="left")
    if merged.empty:
        return merged
    if "ticker" not in merged.columns:
        merged["ticker"] = merged.get("issuer")
    if "trade_date" not in merged.columns:
        merged["trade_date"] = None
    if "directional_label" not in merged.columns:
        merged["directional_label"] = "positive"
    merged["dedupe_trade_date"] = merged["trade_date"].fillna(merged["event_id"])

    merged["strategy_abnormal_return"] = merged.apply(
        lambda row: row["abnormal_vs_xlu"] if row["directional_label"] == "positive" else -row["abnormal_vs_xlu"],
        axis=1,
    )
    merged = merged.sort_values(
        [
            "horizon",
            "ticker",
            "dedupe_trade_date",
            "event_priority",
            "source_confidence",
            "analyst_confidence",
            "event_id",
        ],
        ascending=[True, True, True, False, False, False, True],
    )
    merged = merged.drop_duplicates(subset=["horizon", "ticker", "dedupe_trade_date"], keep="first")
    return merged.drop(columns=["dedupe_trade_date"]).reset_index(drop=True)
