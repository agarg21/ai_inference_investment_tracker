from __future__ import annotations

import csv
import hashlib
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd

from ai_inference_tracker.constants import ANNOTATION_FIELDS, EVENT_TYPES, ISSUER_BY_TICKER, PRIMARY_TICKERS, SIGNAL_VARIANTS
from ai_inference_tracker.db import get_connection, init_db


@dataclass(frozen=True)
class EventRecord:
    event_id: str
    canonical_event_key: str
    event_type: str
    signal_variant: str | None
    issuer: str
    event_timestamp: str | None
    trade_date: str
    region: str | None
    mw_value: float | None
    contract_term_years: float | None
    take_or_pay_pct: float | None
    tariff_type: str | None
    cost_recovery: str | None
    capex_mention: str | None
    source_confidence: int
    analyst_confidence: int
    directional_label: str
    evidence_snippet: str
    notes: str | None
    source_urls: tuple[str, ...]


def ensure_annotation_template(path: Path) -> Path:
    if path.exists():
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ANNOTATION_FIELDS)
        writer.writeheader()
    return path


def _clean_value(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _parse_float(value: str | None) -> float | None:
    cleaned = _clean_value(value)
    if cleaned is None:
        return None
    return float(cleaned)


def _parse_int(value: str | None, default: int = 1) -> int:
    cleaned = _clean_value(value)
    if cleaned is None:
        return default
    return int(cleaned)


def derive_canonical_event_key(row: dict[str, str | None]) -> str:
    explicit = _clean_value(row.get("canonical_event_key"))
    if explicit:
        return explicit
    pieces = [
        _clean_value(row.get("issuer")) or "UNKNOWN",
        _clean_value(row.get("event_type")) or "UNKNOWN",
        (_clean_value(row.get("event_timestamp")) or _clean_value(row.get("trade_date_override")) or "UNKNOWN")[:10],
        _clean_value(row.get("mw_value")) or "na",
        _clean_value(row.get("directional_label")) or "positive",
    ]
    return "::".join(pieces)


def load_annotation_rows(path: Path) -> list[dict[str, str | None]]:
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        rows = [{key: _clean_value(value) for key, value in row.items()} for row in reader]
    return [row for row in rows if any(value for value in row.values())]


def normalize_trade_date(
    *,
    event_timestamp: str | None,
    document_date: str | None,
    trade_date_override: str | None,
    trading_days: Iterable[pd.Timestamp],
) -> str:
    trading_index = pd.DatetimeIndex(pd.to_datetime(list(trading_days))).normalize().unique().sort_values()
    if len(trading_index) == 0:
        raise ValueError("Trading calendar is empty.")

    if trade_date_override:
        target = pd.Timestamp(trade_date_override).normalize()
        idx = trading_index.searchsorted(target)
        if idx >= len(trading_index):
            raise ValueError(f"Trade date override {trade_date_override} is beyond available price history.")
        return trading_index[idx].date().isoformat()

    after_close = False
    if event_timestamp:
        parsed = pd.Timestamp(event_timestamp)
        if parsed.tzinfo is not None:
            parsed = parsed.tz_convert("America/New_York").tz_localize(None)
        target = parsed.normalize()
        after_close = parsed.hour >= 16
    elif document_date:
        target = pd.Timestamp(document_date).normalize()
    else:
        raise ValueError("Either event_timestamp or document_date is required.")

    idx = trading_index.searchsorted(target)
    if idx >= len(trading_index):
        raise ValueError(f"No trading day on or after {target.date().isoformat()}.")
    if after_close and trading_index[idx] == target:
        idx += 1
    if idx >= len(trading_index):
        raise ValueError(f"No next trading day available after {target.date().isoformat()}.")
    return trading_index[idx].date().isoformat()


def _choose_primary_row(rows: list[dict[str, str | None]]) -> dict[str, str | None]:
    ranked = sorted(
        rows,
        key=lambda row: (
            _parse_int(row.get("source_confidence"), default=1),
            _parse_int(row.get("analyst_confidence"), default=1),
            _clean_value(row.get("event_timestamp")) or "",
            _clean_value(row.get("source_url")) or "",
        ),
        reverse=True,
    )
    return ranked[0]


def prepare_event_records(
    rows: list[dict[str, str | None]],
    source_documents: pd.DataFrame,
    trading_days: Iterable[pd.Timestamp],
) -> list[EventRecord]:
    source_lookup = source_documents.set_index("source_url").to_dict("index") if not source_documents.empty else {}
    grouped: dict[str, list[dict[str, str | None]]] = defaultdict(list)
    for row in rows:
        event_type = _clean_value(row.get("event_type"))
        signal_variant = _clean_value(row.get("signal_variant"))
        issuer = _clean_value(row.get("issuer"))
        if event_type not in EVENT_TYPES:
            raise ValueError(f"Unknown event type: {event_type}")
        if signal_variant is not None and signal_variant not in SIGNAL_VARIANTS:
            raise ValueError(f"Unknown signal variant: {signal_variant}")
        if issuer not in PRIMARY_TICKERS:
            raise ValueError(f"Unknown issuer ticker: {issuer}")
        grouped[derive_canonical_event_key(row)].append(row)

    records: list[EventRecord] = []
    for canonical_key, group_rows in grouped.items():
        primary = _choose_primary_row(group_rows)
        source_urls = tuple(sorted({_clean_value(row.get("source_url")) for row in group_rows if _clean_value(row.get("source_url"))}))
        source_row = source_lookup.get(source_urls[0]) if source_urls else None
        event_timestamp = _clean_value(primary.get("event_timestamp"))
        source_confidence = _parse_int(primary.get("source_confidence"), default=1)
        if not event_timestamp and source_row and source_row.get("document_date"):
            source_confidence = max(1, source_confidence - 1)

        trade_date = normalize_trade_date(
            event_timestamp=event_timestamp,
            document_date=(source_row or {}).get("document_date"),
            trade_date_override=_clean_value(primary.get("trade_date_override")),
            trading_days=trading_days,
        )

        event_id = hashlib.sha1(canonical_key.encode("utf-8")).hexdigest()[:16]
        region = _clean_value(primary.get("region")) or ISSUER_BY_TICKER[primary["issuer"]].region
        records.append(
            EventRecord(
                event_id=event_id,
                canonical_event_key=canonical_key,
                event_type=primary["event_type"] or "",
                signal_variant=_clean_value(primary.get("signal_variant")),
                issuer=primary["issuer"] or "",
                event_timestamp=event_timestamp,
                trade_date=trade_date,
                region=region,
                mw_value=_parse_float(primary.get("mw_value")),
                contract_term_years=_parse_float(primary.get("contract_term_years")),
                take_or_pay_pct=_parse_float(primary.get("take_or_pay_pct")),
                tariff_type=_clean_value(primary.get("tariff_type")),
                cost_recovery=_clean_value(primary.get("cost_recovery")),
                capex_mention=_clean_value(primary.get("capex_mention")),
                source_confidence=source_confidence,
                analyst_confidence=_parse_int(primary.get("analyst_confidence"), default=1),
                directional_label=_clean_value(primary.get("directional_label")) or "positive",
                evidence_snippet=_clean_value(primary.get("evidence_snippet")) or "",
                notes=_clean_value(primary.get("notes")),
                source_urls=source_urls,
            )
        )
    return sorted(records, key=lambda record: (record.trade_date, record.issuer, record.event_type))


def persist_events(settings, records: list[EventRecord], source_documents: pd.DataFrame) -> pd.DataFrame:
    init_db(settings)
    with get_connection(settings) as connection:
        if not source_documents.empty:
            for row in source_documents.to_dict("records"):
                source_url = row.get("source_url")
                if not source_url:
                    continue
                source_id = row.get("id")
                connection.execute(
                    """
                    INSERT OR IGNORE INTO source_documents (
                        id,
                        source_url,
                        source_type,
                        issuer_or_region,
                        publish_timestamp,
                        document_date,
                        title,
                        local_snapshot_path,
                        text_snapshot_hash,
                        keyword_score,
                        keyword_hits_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        int(source_id) if source_id is not None else None,
                        source_url,
                        row.get("source_type") or "manual",
                        row.get("issuer_or_region") or row.get("issuer") or "manual",
                        row.get("publish_timestamp"),
                        row.get("document_date"),
                        row.get("title") or source_url,
                        row.get("local_snapshot_path") or "",
                        row.get("text_snapshot_hash") or "manual-placeholder",
                        int(row.get("keyword_score") or 0),
                        row.get("keyword_hits_json") or "[]",
                    ),
                )
        source_id_lookup = {
            db_row["source_url"]: db_row["id"]
            for db_row in connection.execute("SELECT id, source_url FROM source_documents").fetchall()
        }
        connection.execute("DELETE FROM event_source_links")
        connection.execute("DELETE FROM event_tickers")
        connection.execute("DELETE FROM price_windows")
        connection.execute("DELETE FROM trade_cards")
        connection.execute("DELETE FROM events")

        for record in records:
            connection.execute(
                """
                INSERT INTO events (
                    event_id,
                    canonical_event_key,
                    event_type,
                    signal_variant,
                    issuer,
                    event_timestamp,
                    trade_date,
                    region,
                    mw_value,
                    contract_term_years,
                    take_or_pay_pct,
                    tariff_type,
                    cost_recovery,
                    capex_mention,
                    source_confidence,
                    analyst_confidence,
                    directional_label,
                    evidence_snippet,
                    notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.event_id,
                    record.canonical_event_key,
                    record.event_type,
                    record.signal_variant,
                    record.issuer,
                    record.event_timestamp,
                    record.trade_date,
                    record.region,
                    record.mw_value,
                    record.contract_term_years,
                    record.take_or_pay_pct,
                    record.tariff_type,
                    record.cost_recovery,
                    record.capex_mention,
                    record.source_confidence,
                    record.analyst_confidence,
                    record.directional_label,
                    record.evidence_snippet,
                    record.notes,
                ),
            )

            all_tickers = [(record.issuer, "primary"), ("XLU", "benchmark"), ("SPY", "benchmark")]
            all_tickers.extend((ticker, "peer") for ticker in PRIMARY_TICKERS if ticker != record.issuer)
            for ticker, role in all_tickers:
                connection.execute(
                    "INSERT INTO event_tickers (event_id, ticker, role) VALUES (?, ?, ?)",
                    (record.event_id, ticker, role),
                )

            for source_url in record.source_urls:
                source_id = source_id_lookup.get(source_url)
                if source_id is None:
                    continue
                connection.execute(
                    "INSERT INTO event_source_links (event_id, source_document_id) VALUES (?, ?)",
                    (record.event_id, int(source_id)),
                )

    event_df = pd.DataFrame([record.__dict__ for record in records])
    if event_df.empty:
        event_df = pd.DataFrame(
            columns=[
                "event_id",
                "canonical_event_key",
                "event_type",
                "signal_variant",
                "issuer",
                "event_timestamp",
                "trade_date",
                "region",
                "mw_value",
                "contract_term_years",
                "take_or_pay_pct",
                "tariff_type",
                "cost_recovery",
                "capex_mention",
                "source_confidence",
                "analyst_confidence",
                "directional_label",
                "evidence_snippet",
                "notes",
            ]
        )
    else:
        event_df = event_df.drop(columns=["source_urls"])
    return event_df
