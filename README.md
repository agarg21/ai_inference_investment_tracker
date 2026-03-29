# AI Inference Investment Tracker

Local-first Codex research workspace for the AI inference inflection thesis, with publishable static outputs.

## What it does

- Collects free/public source documents into SQLite plus local text snapshots
- Creates a review queue and manual annotation template
- Ingests canonical events from manual annotations
- Runs a daily-price event study against `XLU` and `SPY`
- Generates ranked trade cards and a markdown validation report
- Maintains a structured AI inference thesis tracker and local HTML dashboard
- Writes a publishable `site/` directory for Netlify or any static host

## Scope

- US public equities only
- Free/public sources only
- Daily price horizons: `+1`, `+5`, `+20`, `+60`
- Focus universe:
  - `AEP`
  - `FE`
  - `ETR`
  - `BKH`
  - `PNW`
  - `POR`
  - `IDA`
  - benchmarks `XLU`, `SPY`

## Setup

```bash
cd ai_power_validation
uv venv --python 3.12
source .venv/bin/activate
uv sync --extra dev --no-editable
```

`uv sync --no-editable` is the safest setup on this machine because Python 3.12 is skipping editable `.pth` files that are marked hidden by the virtualenv bootstrap, which breaks the installed console entrypoints.

## Workflow

1. Collect documents and create review assets:

```bash
collect_sources --start-date 2024-01-01
```

For a fast readable-source pass that skips SEC archive bodies:

```bash
collect_sources --mode targeted-readable
```

2. Review `data/outputs/targeted_readable_ready_queue.csv` first for the cleanest manually labelable sources, then use `data/outputs/source_review_queue.csv` if you want the broader corpus. Populate `data/manual_event_annotations.csv`.

3. Run the event study:

```bash
run_event_study
```

4. Build the report:

```bash
build_report
```

5. Build the AI inference tracker:

```bash
build_inference_tracker
```

This writes:

- `data/outputs/inference_tracker.html`
- `data/outputs/inference_tracker.md`
- `site/index.html`
- `site/tracker.md`
- `site/daily-summary.md`

## Outputs

- `data/ai_power_validation.db`
- `data/outputs/source_documents.csv`
- `data/outputs/source_review_queue.csv`
- `data/outputs/targeted_readable_review_queue.csv`
- `data/outputs/targeted_readable_ready_queue.csv`
- `data/outputs/events.csv`
- `data/outputs/event_study.csv`
- `data/outputs/trade_cards.csv`
- `data/outputs/validation_report.md`
- `data/inference_thesis_watchlist.json`
- `data/outputs/inference_tracker.html`
- `data/outputs/inference_tracker.md`
- `site/index.html`
- `site/tracker.md`
- `site/daily-summary.md`
- `data/charts/*.png`

## Netlify

This repo includes [netlify.toml](/Users/apoorvagarg/Documents/Playground/ai_inference_investment_tracker/netlify.toml) with `publish = "site"`.

That means Netlify can serve the committed `site/` folder directly without running the Python build in the cloud yet. The intended workflow for now is:

1. Run the research locally with Codex
2. Rebuild the tracker
3. Commit the refreshed `site/` output
4. Let Netlify publish the latest committed static site
