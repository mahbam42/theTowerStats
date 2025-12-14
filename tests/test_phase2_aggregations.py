"""Golden tests for Phase 2 aggregation helpers."""

from __future__ import annotations

from datetime import date, datetime, timezone

from analysis.aggregations import (
    daily_average_series,
    simple_moving_average,
    summarize_window,
)
from analysis.dto import RunAnalysis


def test_daily_average_series_averages_multiple_runs_per_day() -> None:
    """Aggregate multiple runs on the same day into a daily mean."""

    runs = [
        RunAnalysis(
            run_id=1,
            battle_date=datetime(2025, 12, 1, 1, 0, tzinfo=timezone.utc),
            tier=1,
            preset_name=None,
            coins_per_hour=100.0,
        ),
        RunAnalysis(
            run_id=2,
            battle_date=datetime(2025, 12, 1, 2, 0, tzinfo=timezone.utc),
            tier=1,
            preset_name=None,
            coins_per_hour=300.0,
        ),
        RunAnalysis(
            run_id=3,
            battle_date=datetime(2025, 12, 2, 1, 0, tzinfo=timezone.utc),
            tier=1,
            preset_name=None,
            coins_per_hour=200.0,
        ),
    ]

    series = daily_average_series(runs)
    assert series == {
        "2025-12-01": 200.0,
        "2025-12-02": 200.0,
    }


def test_simple_moving_average_returns_none_when_missing_inputs() -> None:
    """Skip windows that contain missing values instead of assuming zeros."""

    values = [1.0, None, 3.0, 5.0]
    assert simple_moving_average(values, window=2) == [None, None, None, 4.0]


def test_summarize_window_counts_runs_and_averages() -> None:
    """Summarize a date window with run count and mean coins/hour."""

    runs = [
        RunAnalysis(
            run_id=1,
            battle_date=datetime(2025, 12, 1, 0, 0, tzinfo=timezone.utc),
            tier=1,
            preset_name=None,
            coins_per_hour=100.0,
        ),
        RunAnalysis(
            run_id=2,
            battle_date=datetime(2025, 12, 3, 0, 0, tzinfo=timezone.utc),
            tier=1,
            preset_name=None,
            coins_per_hour=300.0,
        ),
    ]

    summary = summarize_window(runs, start_date=date(2025, 12, 1), end_date=date(2025, 12, 2))
    assert summary.run_count == 1
    assert summary.average_coins_per_hour == 100.0

