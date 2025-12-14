"""Golden tests for Phase 1 Analysis Engine behavior."""

from __future__ import annotations

from dataclasses import dataclass
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


def test_analyze_runs_parses_compact_coins_from_raw_text() -> None:
    """Parse `Coins: 4.24M` from raw text and compute coins/hour."""

    @dataclass(frozen=True)
    class Progress:
        battle_date: datetime | None
        wave: int | None
        real_time_seconds: int | None
        coins: int | None = None

    @dataclass(frozen=True)
    class Record:
        raw_text: str
        parsed_at: datetime
        run_progress: Progress

    record = Record(
        raw_text="Battle Report\nCoins: 4.24M\n",
        parsed_at=datetime(2025, 12, 1, 0, 0, tzinfo=timezone.utc),
        run_progress=Progress(battle_date=None, wave=1, real_time_seconds=3600),
    )

    result = analyze_runs([record])
    assert len(result.runs) == 1
    assert result.runs[0].coins_per_hour == 4_240_000.0
