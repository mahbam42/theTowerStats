"""Golden tests for Phase 1 Analysis Engine behavior."""

from __future__ import annotations

from datetime import datetime, timezone

from analysis.engine import analyze_runs
from analysis.dto import RunProgressInput


def test_analyze_runs_computes_waves_per_hour() -> None:
    """Compute waves/hour for a set of run-progress inputs."""

    inputs = [
        RunProgressInput(
            battle_date=datetime(2025, 12, 1, 0, 0, tzinfo=timezone.utc),
            wave=900,
            real_time_seconds=1800,
        ),
        RunProgressInput(
            battle_date=datetime(2025, 12, 2, 0, 0, tzinfo=timezone.utc),
            wave=1800,
            real_time_seconds=3600,
        ),
    ]

    result = analyze_runs(inputs)

    assert len(result.runs) == 2
    assert result.runs[0].waves_per_hour == 1800.0
    assert result.runs[1].waves_per_hour == 1800.0

