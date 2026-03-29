from __future__ import annotations

from datetime import date, timedelta

import pandas as pd
import yfinance as yf

from ai_inference_tracker.constants import BENCHMARK_TICKERS, PRIMARY_TICKERS


def fetch_price_history(start_date: date, end_date: date) -> pd.DataFrame:
    tickers = list(PRIMARY_TICKERS + BENCHMARK_TICKERS)
    download_end = end_date + timedelta(days=90)
    data = yf.download(
        tickers=tickers,
        start=start_date.isoformat(),
        end=download_end.isoformat(),
        auto_adjust=False,
        progress=False,
        group_by="ticker",
    )
    frames: dict[str, pd.Series] = {}
    for ticker in tickers:
        series = None
        try:
            ticker_frame = data[ticker]
            if "Adj Close" in ticker_frame:
                series = ticker_frame["Adj Close"]
            elif "Close" in ticker_frame:
                series = ticker_frame["Close"]
        except Exception:
            if "Adj Close" in data and ticker in data["Adj Close"]:
                series = data["Adj Close"][ticker]
            elif "Close" in data and ticker in data["Close"]:
                series = data["Close"][ticker]
        if series is None:
            raise ValueError(f"Missing price history for {ticker}")
        frames[ticker] = series.dropna()
    price_df = pd.DataFrame(frames).sort_index()
    price_df.index = pd.DatetimeIndex(price_df.index).normalize()
    return price_df
