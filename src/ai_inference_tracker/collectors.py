from __future__ import annotations

import hashlib
import io
import json
import re
import time
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable

import pandas as pd
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader

from ai_inference_tracker.config import Settings
from ai_inference_tracker.constants import ISSUERS, SEC_FORMS, SEC_FORM_LIMITS, SEED_DOCUMENTS, SOURCE_KEYWORDS, TARGETED_READABLE_SEEDS
from ai_inference_tracker.db import get_connection, init_db

PDF_TEXT_PAGE_LIMIT = 15


@dataclass(frozen=True)
class SourceDocument:
    source_url: str
    source_type: str
    issuer_or_region: str
    publish_timestamp: str | None
    document_date: str | None
    title: str
    snapshot_text: str
    keyword_hits: tuple[str, ...]
    fetch_status: str = "ok"
    fetch_error: str | None = None

    @property
    def text_snapshot_hash(self) -> str:
        return hashlib.sha256(self.snapshot_text.encode("utf-8")).hexdigest()


def build_session(user_agent: str) -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": user_agent, "Accept-Encoding": "gzip, deflate"})
    return session


def _extract_text(url: str, content: bytes, content_type: str) -> str:
    lowered_type = (content_type or "").lower()
    if "application/pdf" in lowered_type or url.lower().endswith(".pdf"):
        try:
            reader = PdfReader(io.BytesIO(content))
            page_count = len(reader.pages)
            text = "\n".join(
                (page.extract_text() or "").strip() for page in reader.pages[:PDF_TEXT_PAGE_LIMIT]
            )
            if text.strip():
                if page_count > PDF_TEXT_PAGE_LIMIT:
                    text = (
                        f"[PDF text truncated to first {PDF_TEXT_PAGE_LIMIT} pages of {page_count} total pages]\n"
                        f"{text}"
                    )
                return text
        except Exception:
            pass
        return f"Binary PDF captured from {url}. Manual review required."
    if "application/json" in lowered_type or url.lower().endswith(".json"):
        try:
            payload = json.loads(content.decode("utf-8"))
            return json.dumps(payload, indent=2, sort_keys=True)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return content.decode("utf-8", errors="ignore")
    if any(token in lowered_type for token in ("text/html", "application/xhtml+xml", "application/xml", "text/xml")):
        soup = BeautifulSoup(content, "lxml")
        return "\n".join(line.strip() for line in soup.get_text("\n").splitlines() if line.strip())
    return content.decode("utf-8", errors="ignore")


def fetch_text_snapshot(
    session: requests.Session,
    url: str,
    timeout: int = 30,
    *,
    min_interval_seconds: float = 0.35,
    attempts: int = 3,
) -> tuple[str, str, str | None]:
    last_error: str | None = None
    for attempt in range(attempts):
        if min_interval_seconds > 0:
            time.sleep(min_interval_seconds)
        try:
            response = session.get(url, timeout=timeout)
            response.raise_for_status()
            return _extract_text(url, response.content, response.headers.get("content-type", "")), "ok", None
        except requests.HTTPError as exc:
            last_error = str(exc)
            status_code = exc.response.status_code if exc.response is not None else None
            if status_code == 429 and attempt < attempts - 1:
                time.sleep(1.5 * (attempt + 1))
                continue
            break
        except requests.RequestException as exc:
            last_error = str(exc)
            if attempt < attempts - 1:
                time.sleep(1.5 * (attempt + 1))
                continue
            break
    raise requests.RequestException(last_error or f"Failed to fetch {url}")


def _sec_placeholder_text(issuer: str, form: str, filing_date: str, document_name: str, url: str, error: Exception) -> str:
    return (
        "SEC filing body unavailable from this environment.\n"
        f"Issuer: {issuer}\n"
        f"Form: {form}\n"
        f"Filing date: {filing_date}\n"
        f"Document: {document_name}\n"
        f"URL: {url}\n"
        f"Fetch error: {error}"
    )


def _keyword_hits(text: str) -> tuple[str, ...]:
    lowered = text.lower()
    return tuple(keyword for keyword in SOURCE_KEYWORDS if keyword in lowered)


def _normalize_sec_timestamp(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = value.strip()
    if re.fullmatch(r"\d{14}", cleaned):
        return datetime.strptime(cleaned, "%Y%m%d%H%M%S").isoformat()
    try:
        return pd.Timestamp(cleaned).isoformat()
    except ValueError:
        return None


def _iter_sec_filing_records(session: requests.Session, payload: dict) -> Iterable[dict]:
    filings = payload.get("filings", {})
    recent = filings.get("recent", {})
    fields = list(recent.keys())
    count = len(recent.get("filingDate", []))

    for index in range(count):
        row = {field: recent[field][index] for field in fields}
        yield row

    for extra_file in filings.get("files", []):
        name = extra_file.get("name")
        if not name:
            continue
        extra_url = f"https://data.sec.gov/submissions/{name}"
        response = session.get(extra_url, timeout=30)
        response.raise_for_status()
        extra_payload = response.json()
        extra_recent = extra_payload
        fields = list(extra_recent.keys())
        count = len(extra_recent.get("filingDate", []))
        for index in range(count):
            row = {field: extra_recent[field][index] for field in fields}
            yield row


def collect_sec_documents(
    session: requests.Session,
    start_date: date,
    end_date: date,
) -> list[SourceDocument]:
    documents: dict[str, SourceDocument] = {}
    for issuer in ISSUERS:
        form_counts = {form: 0 for form in SEC_FORM_LIMITS}
        submissions_url = f"https://data.sec.gov/submissions/CIK{issuer.cik}.json"
        response = session.get(submissions_url, timeout=30)
        response.raise_for_status()
        payload = response.json()
        payload["_user_agent"] = session.headers.get("User-Agent", "ai-inference-investment-tracker/0.1")

        for filing in _iter_sec_filing_records(session, payload):
            form = filing.get("form")
            filing_date_raw = filing.get("filingDate")
            if form not in SEC_FORMS or not filing_date_raw:
                continue
            if form == "8-K":
                items = str(filing.get("items") or "")
                if not any(token in items for token in ("2.02", "7.01", "8.01")):
                    continue
            if form_counts.get(form, 0) >= SEC_FORM_LIMITS.get(form, 9999):
                continue

            filing_date = pd.Timestamp(filing_date_raw).date()
            if filing_date < start_date or filing_date > end_date:
                continue

            accession_number = filing.get("accessionNumber", "").replace("-", "")
            primary_document = filing.get("primaryDocument")
            if not accession_number or not primary_document:
                continue

            filing_url = (
                f"https://www.sec.gov/Archives/edgar/data/{int(issuer.cik)}/"
                f"{accession_number}/{primary_document}"
            )
            try:
                snapshot_text, fetch_status, fetch_error = fetch_text_snapshot(session, filing_url)
            except requests.RequestException as exc:
                snapshot_text = _sec_placeholder_text(
                    issuer.ticker,
                    form,
                    filing_date.isoformat(),
                    primary_document,
                    filing_url,
                    exc,
                )
                fetch_status = "error"
                fetch_error = str(exc)
            documents[filing_url] = SourceDocument(
                source_url=filing_url,
                source_type="sec",
                issuer_or_region=issuer.ticker,
                publish_timestamp=_normalize_sec_timestamp(filing.get("acceptanceDateTime")),
                document_date=filing_date.isoformat(),
                title=f"{issuer.ticker} {form} {filing_date.isoformat()}",
                snapshot_text=snapshot_text,
                keyword_hits=_keyword_hits(snapshot_text),
                fetch_status=fetch_status,
                fetch_error=fetch_error,
            )
            form_counts[form] = form_counts.get(form, 0) + 1

            if form != "8-K":
                continue

            index_url = (
                f"https://www.sec.gov/Archives/edgar/data/{int(issuer.cik)}/"
                f"{accession_number}/index.json"
            )
            try:
                index_response = session.get(index_url, timeout=30)
                index_response.raise_for_status()
                index_payload = index_response.json()
            except requests.RequestException:
                continue

            exhibit_count = 0
            for item in index_payload.get("directory", {}).get("item", []):
                name = item.get("name", "")
                lowered = name.lower()
                if "ex99" not in lowered and "99-" not in lowered:
                    continue
                exhibit_count += 1
                if exhibit_count > 2:
                    break
                exhibit_url = (
                    f"https://www.sec.gov/Archives/edgar/data/{int(issuer.cik)}/"
                    f"{accession_number}/{name}"
                )
                try:
                    snapshot_text, fetch_status, fetch_error = fetch_text_snapshot(session, exhibit_url)
                except requests.RequestException as exc:
                    snapshot_text = _sec_placeholder_text(
                        issuer.ticker,
                        "8-K exhibit",
                        filing_date.isoformat(),
                        name,
                        exhibit_url,
                        exc,
                    )
                    fetch_status = "error"
                    fetch_error = str(exc)
                documents[exhibit_url] = SourceDocument(
                    source_url=exhibit_url,
                    source_type="sec_exhibit",
                    issuer_or_region=issuer.ticker,
                    publish_timestamp=_normalize_sec_timestamp(filing.get("acceptanceDateTime")),
                    document_date=filing_date.isoformat(),
                    title=f"{issuer.ticker} 8-K exhibit {name} {filing_date.isoformat()}",
                    snapshot_text=snapshot_text,
                    keyword_hits=_keyword_hits(snapshot_text),
                    fetch_status=fetch_status,
                    fetch_error=fetch_error,
                )
    return sorted(documents.values(), key=lambda item: (item.publish_timestamp or "", item.source_url))


def collect_seed_documents(
    session: requests.Session,
    seeds: Iterable[dict] = SEED_DOCUMENTS,
    *,
    timeout: int = 15,
    attempts: int = 2,
    min_interval_seconds: float = 0.2,
) -> list[SourceDocument]:
    documents: list[SourceDocument] = []
    for seed in seeds:
        try:
            snapshot_text, fetch_status, fetch_error = fetch_text_snapshot(
                session,
                seed["url"],
                timeout=timeout,
                attempts=attempts,
                min_interval_seconds=min_interval_seconds,
            )
        except requests.RequestException as exc:
            snapshot_text = (
                "Source body unavailable from this environment.\n"
                f"Title: {seed['title']}\n"
                f"URL: {seed['url']}\n"
                f"Fetch error: {exc}"
            )
            fetch_status = "error"
            fetch_error = str(exc)
        documents.append(
            SourceDocument(
                source_url=seed["url"],
                source_type=seed["source_type"],
                issuer_or_region=seed["issuer_or_region"],
                publish_timestamp=seed["publish_timestamp"],
                document_date=(seed["publish_timestamp"] or "")[:10] or None,
                title=seed["title"],
                snapshot_text=snapshot_text,
                keyword_hits=_keyword_hits(snapshot_text),
                fetch_status=fetch_status,
                fetch_error=fetch_error,
            )
        )
    return documents


def collect_targeted_readable_documents(session: requests.Session) -> list[SourceDocument]:
    return collect_seed_documents(
        session,
        TARGETED_READABLE_SEEDS,
        timeout=12,
        attempts=1,
        min_interval_seconds=0.1,
    )


def _safe_snapshot_name(title: str, hash_value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return f"{slug[:80] or 'document'}-{hash_value[:12]}.txt"


def store_source_documents(settings: Settings, documents: Iterable[SourceDocument]) -> None:
    init_db(settings)
    with get_connection(settings) as connection:
        for document in documents:
            snapshot_name = _safe_snapshot_name(document.title, document.text_snapshot_hash)
            snapshot_path = settings.snapshots_dir / snapshot_name
            snapshot_path.write_text(document.snapshot_text)
            connection.execute(
                """
                INSERT INTO source_documents (
                    source_url,
                    source_type,
                    issuer_or_region,
                    publish_timestamp,
                    document_date,
                    title,
                    local_snapshot_path,
                    text_snapshot_hash,
                    fetch_status,
                    fetch_error,
                    keyword_score,
                    keyword_hits_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(source_url) DO UPDATE SET
                    source_type = excluded.source_type,
                    issuer_or_region = excluded.issuer_or_region,
                    publish_timestamp = excluded.publish_timestamp,
                    document_date = excluded.document_date,
                    title = excluded.title,
                    local_snapshot_path = excluded.local_snapshot_path,
                    text_snapshot_hash = excluded.text_snapshot_hash,
                    fetch_status = excluded.fetch_status,
                    fetch_error = excluded.fetch_error,
                    keyword_score = excluded.keyword_score,
                    keyword_hits_json = excluded.keyword_hits_json
                """,
                (
                    document.source_url,
                    document.source_type,
                    document.issuer_or_region,
                    document.publish_timestamp,
                    document.document_date,
                    document.title,
                    str(snapshot_path),
                    document.text_snapshot_hash,
                    document.fetch_status,
                    document.fetch_error,
                    len(document.keyword_hits),
                    json.dumps(document.keyword_hits),
                ),
            )


def prune_source_documents(settings: Settings, *, source_types: Iterable[str], keep_urls: Iterable[str]) -> None:
    init_db(settings)
    normalized_source_types = tuple(dict.fromkeys(source_types))
    keep_url_set = set(keep_urls)
    if not normalized_source_types:
        return
    placeholders = ", ".join("?" for _ in normalized_source_types)
    with get_connection(settings) as connection:
        rows = connection.execute(
            f"""
            SELECT source_url, local_snapshot_path
            FROM source_documents
            WHERE source_type IN ({placeholders})
            """,
            normalized_source_types,
        ).fetchall()
        stale_rows = [row for row in rows if row["source_url"] not in keep_url_set]
        for row in stale_rows:
            snapshot_path = Path(row["local_snapshot_path"])
            if snapshot_path.exists():
                snapshot_path.unlink()
        if stale_rows:
            stale_urls = [row["source_url"] for row in stale_rows]
            url_placeholders = ", ".join("?" for _ in stale_urls)
            connection.execute(
                f"DELETE FROM source_documents WHERE source_url IN ({url_placeholders})",
                stale_urls,
            )


def export_source_outputs(settings: Settings) -> tuple[Path, Path]:
    with get_connection(settings) as connection:
        source_df = pd.read_sql_query(
            """
            SELECT
                id,
                source_url,
                source_type,
                issuer_or_region,
                publish_timestamp,
                document_date,
                title,
                local_snapshot_path,
                text_snapshot_hash,
                fetch_status,
                fetch_error,
                keyword_score,
                keyword_hits_json,
                retrieved_at
            FROM source_documents
            ORDER BY publish_timestamp DESC, issuer_or_region, title
            """,
            connection,
        )
    source_csv = settings.outputs_dir / "source_documents.csv"
    source_df.to_csv(source_csv, index=False)

    review_df = source_df.copy()
    review_df["matched_keywords"] = review_df["keyword_hits_json"].apply(lambda value: ", ".join(json.loads(value)))
    review_df = review_df[
        [
            "id",
            "issuer_or_region",
            "source_type",
            "publish_timestamp",
            "document_date",
            "title",
            "fetch_status",
            "fetch_error",
            "keyword_score",
            "matched_keywords",
            "source_url",
            "local_snapshot_path",
        ]
    ]
    review_csv = settings.outputs_dir / "source_review_queue.csv"
    review_df.to_csv(review_csv, index=False)
    return source_csv, review_csv


def export_targeted_review_queue(settings: Settings) -> Path:
    with get_connection(settings) as connection:
        targeted_df = pd.read_sql_query(
            """
            SELECT
                id,
                issuer_or_region,
                source_type,
                publish_timestamp,
                document_date,
                title,
                fetch_status,
                fetch_error,
                keyword_score,
                keyword_hits_json,
                source_url,
                local_snapshot_path
            FROM source_documents
            WHERE source_type IN ('issuer_ir', 'pjm', 'ercot', 'eia')
            ORDER BY keyword_score DESC, publish_timestamp DESC, issuer_or_region
            """,
            connection,
        )
    if targeted_df.empty:
        targeted_df = pd.DataFrame(
            columns=[
                "id",
                "issuer_or_region",
                "source_type",
                "publish_timestamp",
                "document_date",
                "title",
                "fetch_status",
                "fetch_error",
                "keyword_score",
                "keyword_hits_json",
                "source_url",
                "local_snapshot_path",
            ]
        )
    targeted_df["matched_keywords"] = targeted_df["keyword_hits_json"].apply(
        lambda value: ", ".join(json.loads(value)) if isinstance(value, str) else ""
    )
    targeted_df = targeted_df[
        [
            "id",
            "issuer_or_region",
            "source_type",
            "publish_timestamp",
            "document_date",
            "title",
            "fetch_status",
            "fetch_error",
            "keyword_score",
            "matched_keywords",
            "source_url",
            "local_snapshot_path",
        ]
    ]
    output_path = settings.outputs_dir / "targeted_readable_review_queue.csv"
    targeted_df.to_csv(output_path, index=False)
    ready_df = targeted_df[
        (targeted_df["fetch_status"] == "ok") & (targeted_df["keyword_score"] > 0)
    ].copy()
    ready_output_path = settings.outputs_dir / "targeted_readable_ready_queue.csv"
    ready_df.to_csv(ready_output_path, index=False)
    return output_path
