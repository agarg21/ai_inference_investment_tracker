from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from ai_inference_tracker.annotations import ensure_annotation_template
from ai_inference_tracker.collectors import (
    build_session,
    collect_sec_documents,
    collect_seed_documents,
    collect_targeted_readable_documents,
    export_source_outputs,
    export_targeted_review_queue,
    prune_source_documents,
    store_source_documents,
)
from ai_inference_tracker.config import load_settings
from ai_inference_tracker.constants import ISSUER_SEED_DOCUMENTS
from ai_inference_tracker.event_study import run_event_study
from ai_inference_tracker.inference_tracker import build_inference_tracker
from ai_inference_tracker.reporting import build_report


def _parse_args() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI inference investment research toolkit")
    parser.add_argument("--mode", choices=["full", "targeted-readable"], default="full")
    parser.add_argument("--start-date", default="2024-01-01")
    parser.add_argument("--end-date", default=date.today().isoformat())
    parser.add_argument(
        "--annotations-path",
        default=None,
        help="Path to manual event annotations CSV. Defaults to data/manual_event_annotations.csv",
    )
    return parser


def collect_sources_main() -> None:
    parser = _parse_args()
    args = parser.parse_args()
    settings = load_settings()
    session = build_session(settings.user_agent)
    start_date = date.fromisoformat(args.start_date)
    end_date = date.fromisoformat(args.end_date)

    if args.mode == "targeted-readable":
        documents = collect_targeted_readable_documents(session)
        prune_source_documents(
            settings,
            source_types=("issuer_ir", "pjm", "ercot", "eia"),
            keep_urls=(document.source_url for document in documents),
        )
    else:
        documents = []
        documents.extend(collect_sec_documents(session, start_date, end_date))
        documents.extend(collect_seed_documents(session))
        documents.extend(collect_seed_documents(session, ISSUER_SEED_DOCUMENTS))
    store_source_documents(settings, documents)
    source_csv, review_csv = export_source_outputs(settings)
    targeted_review_csv = export_targeted_review_queue(settings)

    annotations_path = Path(args.annotations_path) if args.annotations_path else settings.data_dir / "manual_event_annotations.csv"
    ensure_annotation_template(annotations_path)
    print(f"Stored {len(documents)} source documents.")
    print(f"Source export: {source_csv}")
    print(f"Review queue: {review_csv}")
    print(f"Targeted readable queue: {targeted_review_csv}")
    print(f"Annotation template: {annotations_path}")


def run_event_study_main() -> None:
    parser = _parse_args()
    args = parser.parse_args()
    settings = load_settings()
    annotations_path = Path(args.annotations_path) if args.annotations_path else settings.data_dir / "manual_event_annotations.csv"
    events_df, price_windows_df, trade_cards_df = run_event_study(settings, annotations_path)
    print(f"Ingested {len(events_df)} canonical events.")
    print(f"Computed {len(price_windows_df)} event-study rows.")
    print(f"Qualified {len(trade_cards_df)} trade cards.")


def build_report_main() -> None:
    settings = load_settings()
    report_path = build_report(settings)
    print(f"Report written to {report_path}")


def build_inference_tracker_main() -> None:
    settings = load_settings()
    html_path, md_path = build_inference_tracker(settings)
    print(f"HTML tracker written to {html_path}")
    print(f"Markdown tracker written to {md_path}")
