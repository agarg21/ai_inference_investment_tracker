from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    root_dir: Path
    data_dir: Path
    outputs_dir: Path
    snapshots_dir: Path
    charts_dir: Path
    database_path: Path
    user_agent: str


def _resolve_root_dir() -> Path:
    env_root = os.getenv("AI_INFERENCE_TRACKER_ROOT") or os.getenv("AI_POWER_VALIDATION_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()

    cwd = Path.cwd().resolve()
    for candidate in (cwd, *cwd.parents):
        if (candidate / "pyproject.toml").exists() and (candidate / "src" / "ai_inference_tracker").exists():
            return candidate

    return Path(__file__).resolve().parents[2]


def load_settings() -> Settings:
    root_dir = _resolve_root_dir()
    data_dir = root_dir / "data"
    outputs_dir = data_dir / "outputs"
    snapshots_dir = data_dir / "snapshots"
    charts_dir = data_dir / "charts"
    database_path = (data_dir / "ai_inference_tracker.db").resolve()
    legacy_database_path = (data_dir / "ai_power_validation.db").resolve()

    for path in (data_dir, outputs_dir, snapshots_dir, charts_dir):
        path.mkdir(parents=True, exist_ok=True)

    if not database_path.exists() and legacy_database_path.exists():
        shutil.copy2(legacy_database_path, database_path)

    return Settings(
        root_dir=root_dir,
        data_dir=data_dir,
        outputs_dir=outputs_dir,
        snapshots_dir=snapshots_dir,
        charts_dir=charts_dir,
        database_path=database_path,
        user_agent=os.getenv(
            "AI_INFERENCE_TRACKER_USER_AGENT",
            os.getenv(
                "AI_POWER_VALIDATION_USER_AGENT",
                "Apoorva Garg Research contact-needed@example.com",
            ),
        ),
    )
