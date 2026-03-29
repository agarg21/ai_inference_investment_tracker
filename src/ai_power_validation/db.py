from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from importlib import resources
from pathlib import Path
from typing import Iterator

from ai_power_validation.config import Settings


def connect(database_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(str(database_path))
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db(settings: Settings) -> None:
    schema = resources.files("ai_power_validation").joinpath("schema.sql").read_text()
    with connect(settings.database_path) as connection:
        connection.executescript(schema)
        columns = {row["name"] for row in connection.execute("PRAGMA table_info(source_documents)").fetchall()}
        if "fetch_status" not in columns:
            try:
                connection.execute("ALTER TABLE source_documents ADD COLUMN fetch_status TEXT NOT NULL DEFAULT 'ok'")
            except sqlite3.OperationalError as exc:
                if "duplicate column name" not in str(exc).lower():
                    raise
        if "fetch_error" not in columns:
            try:
                connection.execute("ALTER TABLE source_documents ADD COLUMN fetch_error TEXT")
            except sqlite3.OperationalError as exc:
                if "duplicate column name" not in str(exc).lower():
                    raise
        event_columns = {row["name"] for row in connection.execute("PRAGMA table_info(events)").fetchall()}
        if "signal_variant" not in event_columns:
            try:
                connection.execute("ALTER TABLE events ADD COLUMN signal_variant TEXT")
            except sqlite3.OperationalError as exc:
                if "duplicate column name" not in str(exc).lower():
                    raise
        connection.execute(
            "CREATE INDEX IF NOT EXISTS events_signal_variant_trade_date_idx "
            "ON events(signal_variant, trade_date DESC)"
        )
        connection.commit()


@contextmanager
def get_connection(settings: Settings) -> Iterator[sqlite3.Connection]:
    connection = connect(settings.database_path)
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()
