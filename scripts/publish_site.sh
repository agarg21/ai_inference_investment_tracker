#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

export XDG_CACHE_HOME="${XDG_CACHE_HOME:-$ROOT_DIR/.cache}"
mkdir -p "$XDG_CACHE_HOME"

build_tracker_with_python() {
  local python_bin="${1:-python3}"
  PYTHONPATH="$ROOT_DIR/src${PYTHONPATH:+:$PYTHONPATH}" "$python_bin" - <<'PY'
from ai_inference_tracker.config import load_settings
from ai_inference_tracker.inference_tracker import build_inference_tracker

settings = load_settings()
html_path, md_path = build_inference_tracker(settings)
print(f"HTML tracker written to {html_path}")
print(f"Markdown tracker written to {md_path}")
PY
}

build_tracker() {
  if command -v uv >/dev/null 2>&1; then
    if [[ ! -d ".venv" ]]; then
      uv sync --extra dev --no-editable
    fi

    if uv sync --extra dev --no-editable --reinstall-package ai-inference-investment-tracker >/dev/null 2>&1; then
      if [[ -x ".venv/bin/build_inference_tracker" ]]; then
        ./.venv/bin/build_inference_tracker
        return
      fi
    else
      echo "uv sync failed; falling back to direct Python build." >&2
    fi
  fi

  if [[ -x ".venv/bin/python" ]]; then
    build_tracker_with_python ".venv/bin/python"
    return
  fi

  if command -v python3 >/dev/null 2>&1; then
    build_tracker_with_python "python3"
    return
  fi

  echo "Could not find uv or python3 to build the inference tracker." >&2
  exit 1
}

build_tracker

if ! git diff --quiet -- site data/outputs/inference_tracker.html data/outputs/inference_tracker.md data/outputs/inference_daily_summary.md data/inference_thesis_watchlist.json data/inference_demand_dashboard.json; then
  git add site data/outputs/inference_tracker.html data/outputs/inference_tracker.md data/outputs/inference_daily_summary.md data/inference_thesis_watchlist.json data/inference_demand_dashboard.json
  git commit -m "Refresh inference tracker"
  git push origin HEAD:main
else
  echo "No publishable changes detected."
fi
