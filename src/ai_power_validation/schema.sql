CREATE TABLE IF NOT EXISTS source_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_url TEXT NOT NULL UNIQUE,
    source_type TEXT NOT NULL,
    issuer_or_region TEXT NOT NULL,
    publish_timestamp TEXT,
    document_date TEXT,
    title TEXT NOT NULL,
    local_snapshot_path TEXT NOT NULL,
    text_snapshot_hash TEXT NOT NULL,
    fetch_status TEXT NOT NULL DEFAULT 'ok',
    fetch_error TEXT,
    keyword_score INTEGER NOT NULL DEFAULT 0,
    keyword_hits_json TEXT NOT NULL DEFAULT '[]',
    retrieved_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS events (
    event_id TEXT PRIMARY KEY,
    canonical_event_key TEXT NOT NULL UNIQUE,
    event_type TEXT NOT NULL,
    signal_variant TEXT,
    issuer TEXT NOT NULL,
    event_timestamp TEXT,
    trade_date TEXT NOT NULL,
    region TEXT,
    mw_value REAL,
    contract_term_years REAL,
    take_or_pay_pct REAL,
    tariff_type TEXT,
    cost_recovery TEXT,
    capex_mention TEXT,
    source_confidence INTEGER NOT NULL,
    analyst_confidence INTEGER NOT NULL,
    directional_label TEXT NOT NULL,
    evidence_snippet TEXT NOT NULL,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS event_source_links (
    event_id TEXT NOT NULL,
    source_document_id INTEGER NOT NULL,
    PRIMARY KEY (event_id, source_document_id),
    FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE,
    FOREIGN KEY (source_document_id) REFERENCES source_documents(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS event_tickers (
    event_id TEXT NOT NULL,
    ticker TEXT NOT NULL,
    role TEXT NOT NULL,
    PRIMARY KEY (event_id, ticker, role),
    FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS price_windows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT NOT NULL,
    ticker TEXT NOT NULL,
    horizon INTEGER NOT NULL,
    window_end_date TEXT NOT NULL,
    raw_return REAL NOT NULL,
    benchmark_xlu_return REAL NOT NULL,
    benchmark_spy_return REAL NOT NULL,
    abnormal_vs_xlu REAL NOT NULL,
    abnormal_vs_spy REAL NOT NULL,
    FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS trade_cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    direction TEXT NOT NULL,
    horizon INTEGER NOT NULL,
    hit_rate REAL NOT NULL,
    median_abnormal_return REAL NOT NULL,
    sample_count INTEGER NOT NULL,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS source_documents_type_timestamp_idx
    ON source_documents(source_type, publish_timestamp DESC);

CREATE INDEX IF NOT EXISTS events_type_trade_date_idx
    ON events(event_type, trade_date DESC);

CREATE INDEX IF NOT EXISTS price_windows_event_horizon_idx
    ON price_windows(event_id, horizon);
