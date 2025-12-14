"""Golden tests for Phase 1 Analysis Engine behavior."""

from __future__ import annotations

from datetime import datetime, timezone

from analysis.engine import analyze_runs
from analysis.dto import RunProgressInput


def test_analyze_runs_computes_coins_per_hour() -> None:
    """Compute coins/hour for a set of run-progress inputs."""

    inputs = [
        RunProgressInput(
            battle_date=datetime(2025, 12, 1, 0, 0, tzinfo=timezone.utc),
            coins=900_000,
            wave=900,
            real_time_seconds=1800,
        ),
        RunProgressInput(
            battle_date=datetime(2025, 12, 2, 0, 0, tzinfo=timezone.utc),
            coins=1_800_000,
            wave=1800,
            real_time_seconds=3600,
        ),
    ]

    result = analyze_runs(inputs)

    assert len(result.runs) == 2
    assert result.runs[0].coins_per_hour == 1_800_000.0
    assert result.runs[1].coins_per_hour == 1_800_000.0
