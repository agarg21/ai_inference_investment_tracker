#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -d ".venv" ]]; then
  uv sync --extra dev --no-editable
fi

./.venv/bin/build_inference_tracker

if ! git diff --quiet -- site data/outputs/inference_tracker.html data/outputs/inference_tracker.md data/outputs/inference_daily_summary.md data/inference_thesis_watchlist.json; then
  git add site data/outputs/inference_tracker.html data/outputs/inference_tracker.md data/outputs/inference_daily_summary.md data/inference_thesis_watchlist.json
  git commit -m "Refresh inference tracker"
  git push origin main
else
  echo "No publishable changes detected."
fi
