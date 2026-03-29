from __future__ import annotations

from pathlib import Path

import pytest

from ai_power_validation.config import Settings
from ai_power_validation.db import init_db


@pytest.fixture()
def settings(tmp_path: Path) -> Settings:
    data_dir = tmp_path / "data"
    outputs_dir = data_dir / "outputs"
    snapshots_dir = data_dir / "snapshots"
    charts_dir = data_dir / "charts"
    for path in (data_dir, outputs_dir, snapshots_dir, charts_dir):
        path.mkdir(parents=True, exist_ok=True)

    settings = Settings(
        root_dir=Path(__file__).resolve().parents[1],
        data_dir=data_dir,
        outputs_dir=outputs_dir,
        snapshots_dir=snapshots_dir,
        charts_dir=charts_dir,
        database_path=data_dir / "test.db",
        user_agent="test-agent",
    )
    init_db(settings)
    return settings
