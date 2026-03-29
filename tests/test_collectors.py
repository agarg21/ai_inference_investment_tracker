from __future__ import annotations

from datetime import date

from ai_power_validation.collectors import (
    SourceDocument,
    collect_sec_documents,
    collect_seed_documents,
    prune_source_documents,
    store_source_documents,
)
from ai_power_validation.db import get_connection


class FakeResponse:
    def __init__(self, *, json_data=None, text="", content_type="text/html"):
        self._json_data = json_data
        self.content = text.encode("utf-8")
        self.headers = {"content-type": content_type}

    def json(self):
        if self._json_data is None:
            raise ValueError("No JSON payload")
        return self._json_data

    def raise_for_status(self):
        return None


class FakeSession:
    def __init__(self, responses):
        self.responses = responses
        self.headers = {"User-Agent": "test-agent"}

    def get(self, url, timeout=30):
        return self.responses[url]


def test_collect_sec_documents_returns_metadata_and_text():
    submissions = {
        "filings": {
            "recent": {
                "filingDate": ["2025-02-17"],
                "acceptanceDateTime": ["20250217160500"],
                "form": ["8-K"],
                "items": ["2.02,7.01"],
                "accessionNumber": ["0001031296-26-000041"],
                "primaryDocument": ["factbook.htm"],
            },
            "files": [],
        }
    }
    responses = {
        "https://data.sec.gov/submissions/CIK0000004904.json": FakeResponse(json_data={"filings": {"recent": {"filingDate": [], "acceptanceDateTime": [], "form": [], "items": [], "accessionNumber": [], "primaryDocument": []}, "files": []}}),
        "https://data.sec.gov/submissions/CIK0001031296.json": FakeResponse(json_data=submissions),
        "https://data.sec.gov/submissions/CIK0000065984.json": FakeResponse(json_data={"filings": {"recent": {"filingDate": [], "acceptanceDateTime": [], "form": [], "items": [], "accessionNumber": [], "primaryDocument": []}, "files": []}}),
        "https://data.sec.gov/submissions/CIK0001130464.json": FakeResponse(json_data={"filings": {"recent": {"filingDate": [], "acceptanceDateTime": [], "form": [], "items": [], "accessionNumber": [], "primaryDocument": []}, "files": []}}),
        "https://data.sec.gov/submissions/CIK0000764622.json": FakeResponse(json_data={"filings": {"recent": {"filingDate": [], "acceptanceDateTime": [], "form": [], "items": [], "accessionNumber": [], "primaryDocument": []}, "files": []}}),
        "https://data.sec.gov/submissions/CIK0000784977.json": FakeResponse(json_data={"filings": {"recent": {"filingDate": [], "acceptanceDateTime": [], "form": [], "items": [], "accessionNumber": [], "primaryDocument": []}, "files": []}}),
        "https://data.sec.gov/submissions/CIK0001057877.json": FakeResponse(json_data={"filings": {"recent": {"filingDate": [], "acceptanceDateTime": [], "form": [], "items": [], "accessionNumber": [], "primaryDocument": []}, "files": []}}),
        "https://www.sec.gov/Archives/edgar/data/1031296/000103129626000041/factbook.htm": FakeResponse(text="<html><title>FE Fact Book</title><body>Contracted data center load and tariff updates.</body></html>"),
        "https://www.sec.gov/Archives/edgar/data/1031296/000103129626000041/index.json": FakeResponse(
            json_data={"directory": {"item": [{"name": "ex99.htm"}]}},
            content_type="application/json",
        ),
        "https://www.sec.gov/Archives/edgar/data/1031296/000103129626000041/ex99.htm": FakeResponse(text="<html><body>Pipeline MW increased.</body></html>"),
    }
    session = FakeSession(responses)
    documents = collect_sec_documents(session, date(2024, 1, 1), date(2026, 12, 31))
    assert len(documents) == 2
    assert documents[0].source_type in {"sec", "sec_exhibit"}
    assert any("tariff updates" in doc.snapshot_text for doc in documents)
    assert any("pipeline mw increased" in doc.snapshot_text.lower() for doc in documents)


def test_collect_seed_documents_returns_text_for_pjm_and_ercot():
    responses = {
        "https://insidelines.pjm.com/2025-year-in-review-planning-prepares-for-burgeoning-electricity-demand/": FakeResponse(
            text="<html><body>PJM load growth and data center demand.</body></html>"
        ),
        "https://www.ercot.com/news/release/12122025-ercot-announces-strategic": FakeResponse(
            text="<html><body>ERCOT large load progress.</body></html>"
        ),
        "https://www.ercot.com/files/docs/2025/12/24/Large-Load-Interconnection-Process-Q-A.pdf": FakeResponse(
            text="binary-pdf",
            content_type="application/pdf",
        ),
        "https://www.eia.gov/pressroom/releases/press582.php": FakeResponse(
            text="<html><body>EIA expects data center demand growth.</body></html>"
        ),
        "https://data.ferc.gov/company-registration/ferc-company-identifier-listing/": FakeResponse(
            text="<html><body>FERC identifier listing.</body></html>"
        ),
    }
    session = FakeSession(responses)
    documents = collect_seed_documents(session)
    assert any(doc.source_type == "pjm" and "data center demand" in doc.snapshot_text.lower() for doc in documents)
    assert any(doc.source_type == "ercot" and "manual review required" in doc.snapshot_text.lower() for doc in documents)


def test_store_source_documents_persists_snapshot_and_metadata(settings):
    document = SourceDocument(
        source_url="https://example.com/doc",
        source_type="pjm",
        issuer_or_region="PJM",
        publish_timestamp="2026-01-08T00:00:00-05:00",
        document_date="2026-01-08",
        title="Example PJM Doc",
        snapshot_text="Large load and tariff data center updates.",
        keyword_hits=("large load", "tariff"),
    )
    store_source_documents(settings, [document])
    snapshots = list(settings.snapshots_dir.glob("*.txt"))
    assert len(snapshots) == 1


def test_prune_source_documents_removes_stale_rows_and_snapshots(settings):
    stale_document = SourceDocument(
        source_url="https://example.com/stale",
        source_type="issuer_ir",
        issuer_or_region="POR",
        publish_timestamp="2025-02-14T00:00:00-08:00",
        document_date="2025-02-14",
        title="Stale Doc",
        snapshot_text="stale",
        keyword_hits=(),
    )
    fresh_document = SourceDocument(
        source_url="https://example.com/fresh",
        source_type="issuer_ir",
        issuer_or_region="AEP",
        publish_timestamp="2025-07-31T00:00:00-04:00",
        document_date="2025-07-31",
        title="Fresh Doc",
        snapshot_text="fresh",
        keyword_hits=("data center",),
    )
    store_source_documents(settings, [stale_document, fresh_document])
    prune_source_documents(
        settings,
        source_types=("issuer_ir",),
        keep_urls=(fresh_document.source_url,),
    )

    with get_connection(settings) as connection:
        urls = {
            row["source_url"]
            for row in connection.execute("SELECT source_url FROM source_documents").fetchall()
        }
    assert urls == {fresh_document.source_url}
    snapshots = sorted(path.read_text() for path in settings.snapshots_dir.glob("*.txt"))
    assert snapshots == ["fresh"]
