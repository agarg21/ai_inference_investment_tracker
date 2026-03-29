from __future__ import annotations

from datetime import date

import pandas as pd

from ai_inference_tracker.annotations import ensure_annotation_template, load_annotation_rows, persist_events, prepare_event_records
from ai_inference_tracker.config import Settings
from ai_inference_tracker.constants import FORWARD_HORIZONS
from ai_inference_tracker.db import get_connection, init_db
from ai_inference_tracker.prices import fetch_price_history
from ai_inference_tracker.strategy import build_strategy_windows


def load_source_documents(settings: Settings) -> pd.DataFrame:
    init_db(settings)
    with get_connection(settings) as connection:
        source_documents = pd.read_sql_query("SELECT * FROM source_documents ORDER BY publish_timestamp DESC", connection)
    if not source_documents.empty:
        return source_documents

    source_csv = settings.outputs_dir / "source_documents.csv"
    if source_csv.exists():
        fallback_documents = pd.read_csv(source_csv)
        if not fallback_documents.empty:
            return fallback_documents
    return source_documents


def compute_price_windows(events_df: pd.DataFrame, prices_df: pd.DataFrame) -> pd.DataFrame:
    if events_df.empty:
        return pd.DataFrame(
            columns=[
                "event_id",
                "ticker",
                "horizon",
                "window_end_date",
                "raw_return",
                "benchmark_xlu_return",
                "benchmark_spy_return",
                "abnormal_vs_xlu",
                "abnormal_vs_spy",
            ]
        )
    rows: list[dict[str, object]] = []
    trading_index = pd.DatetimeIndex(prices_df.index).normalize()
    for event in events_df.to_dict("records"):
        ticker = event["issuer"]
        trade_date = pd.Timestamp(event["trade_date"]).normalize()
        event_idx = trading_index.get_loc(trade_date)
        event_price = float(prices_df.loc[trade_date, ticker])
        xlu_price = float(prices_df.loc[trade_date, "XLU"])
        spy_price = float(prices_df.loc[trade_date, "SPY"])
        for horizon in FORWARD_HORIZONS:
            forward_idx = event_idx + horizon
            if forward_idx >= len(trading_index):
                continue
            window_end = trading_index[forward_idx]
            forward_price = float(prices_df.iloc[forward_idx][ticker])
            xlu_forward = float(prices_df.iloc[forward_idx]["XLU"])
            spy_forward = float(prices_df.iloc[forward_idx]["SPY"])
            raw_return = forward_price / event_price - 1.0
            benchmark_xlu_return = xlu_forward / xlu_price - 1.0
            benchmark_spy_return = spy_forward / spy_price - 1.0
            rows.append(
                {
                    "event_id": event["event_id"],
                    "ticker": ticker,
                    "horizon": horizon,
                    "window_end_date": window_end.date().isoformat(),
                    "raw_return": raw_return,
                    "benchmark_xlu_return": benchmark_xlu_return,
                    "benchmark_spy_return": benchmark_spy_return,
                    "abnormal_vs_xlu": raw_return - benchmark_xlu_return,
                    "abnormal_vs_spy": raw_return - benchmark_spy_return,
                }
            )
    return pd.DataFrame(rows)


def build_trade_cards(events_df: pd.DataFrame, price_windows_df: pd.DataFrame) -> pd.DataFrame:
    merged = build_strategy_windows(events_df, price_windows_df)
    if merged.empty:
        return pd.DataFrame(
            columns=["event_type", "direction", "horizon", "hit_rate", "median_abnormal_return", "sample_count", "notes"]
        )

    merged["direction"] = merged["directional_label"].map({"positive": "long", "negative": "short"}).fillna("long")

    grouped_rows: list[dict[str, object]] = []
    grouped = merged.groupby(["event_type", "direction", "horizon"], dropna=False)
    for (event_type, direction, horizon), frame in grouped:
        sample_count = int(len(frame))
        hit_rate = float((frame["strategy_abnormal_return"] > 0).mean()) if sample_count else 0.0
        median_abnormal = float(frame["strategy_abnormal_return"].median()) if sample_count else 0.0
        if sample_count < 8 or horizon not in (20, 60) or median_abnormal <= 0 or hit_rate <= 0.55:
            continue
        grouped_rows.append(
            {
                "event_type": event_type,
                "direction": direction,
                "horizon": int(horizon),
                "hit_rate": hit_rate,
                "median_abnormal_return": median_abnormal,
                "sample_count": sample_count,
                "notes": "Qualified against XLU-relative thresholds in v1.",
            }
        )

    if not grouped_rows:
        return pd.DataFrame(
            columns=["event_type", "direction", "horizon", "hit_rate", "median_abnormal_return", "sample_count", "notes"]
        )
    return pd.DataFrame(grouped_rows).sort_values(
        ["median_abnormal_return", "hit_rate", "sample_count"], ascending=[False, False, False]
    )


def store_price_windows(settings: Settings, price_windows_df: pd.DataFrame, trade_cards_df: pd.DataFrame) -> None:
    with get_connection(settings) as connection:
        connection.execute("DELETE FROM price_windows")
        connection.execute("DELETE FROM trade_cards")

        for row in price_windows_df.to_dict("records"):
            connection.execute(
                """
                INSERT INTO price_windows (
                    event_id,
                    ticker,
                    horizon,
                    window_end_date,
                    raw_return,
                    benchmark_xlu_return,
                    benchmark_spy_return,
                    abnormal_vs_xlu,
                    abnormal_vs_spy
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["event_id"],
                    row["ticker"],
                    int(row["horizon"]),
                    row["window_end_date"],
                    float(row["raw_return"]),
                    float(row["benchmark_xlu_return"]),
                    float(row["benchmark_spy_return"]),
                    float(row["abnormal_vs_xlu"]),
                    float(row["abnormal_vs_spy"]),
                ),
            )

        for row in trade_cards_df.to_dict("records"):
            connection.execute(
                """
                INSERT INTO trade_cards (
                    event_type,
                    direction,
                    horizon,
                    hit_rate,
                    median_abnormal_return,
                    sample_count,
                    notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["event_type"],
                    row["direction"],
                    int(row["horizon"]),
                    float(row["hit_rate"]),
                    float(row["median_abnormal_return"]),
                    int(row["sample_count"]),
                    row["notes"],
                ),
            )


def run_event_study(settings: Settings, annotations_path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ensure_annotation_template(annotations_path)
    rows = load_annotation_rows(annotations_path)
    source_documents = load_source_documents(settings)
    if source_documents.empty:
        raise ValueError("No source documents found. Run collect_sources first.")

    document_dates = source_documents["document_date"].dropna()
    earliest_date = pd.Timestamp(document_dates.min()).date() if not document_dates.empty else date(2024, 1, 1)
    latest_date = pd.Timestamp(date.today()).date()
    prices_df = fetch_price_history(earliest_date, latest_date)

    events = prepare_event_records(rows, source_documents, prices_df.index)
    events_df = persist_events(settings, events, source_documents)
    price_windows_df = compute_price_windows(events_df, prices_df)
    trade_cards_df = build_trade_cards(events_df, price_windows_df)
    store_price_windows(settings, price_windows_df, trade_cards_df)
    events_df.to_csv(settings.outputs_dir / "events.csv", index=False)
    price_windows_df.to_csv(settings.outputs_dir / "event_study.csv", index=False)
    trade_cards_df.to_csv(settings.outputs_dir / "trade_cards.csv", index=False)
    return events_df, price_windows_df, trade_cards_df
