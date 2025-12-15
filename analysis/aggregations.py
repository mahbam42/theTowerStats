"""Aggregation helpers for the Analysis Engine.

This module provides deterministic, reusable aggregation functions used by the
UI (charts, comparisons) without introducing Django dependencies.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Sequence
from datetime import date
from typing import Callable

from .dto import RunAnalysis, WindowSummary


def filter_runs_by_date(
    runs: Iterable[RunAnalysis],
    *,
    start_date: date | None,
    end_date: date | None,
) -> tuple[RunAnalysis, ...]:
    """Filter analyzed runs by an inclusive date range.

    Args:
        runs: Per-run analysis results.
        start_date: Optional start date (inclusive).
        end_date: Optional end date (inclusive).

    Returns:
        A tuple of runs whose `battle_date.date()` falls within the given range.
    """

    filtered: list[RunAnalysis] = []
    for run in runs:
        run_date = run.battle_date.date()
        if start_date is not None and run_date < start_date:
            continue
        if end_date is not None and run_date > end_date:
            continue
        filtered.append(run)
    return tuple(filtered)


def average_coins_per_hour(runs: Iterable[RunAnalysis]) -> float | None:
    """Compute average coins/hour across runs.

    Args:
        runs: Per-run analysis results.

    Returns:
        The arithmetic mean of `coins_per_hour`, or None when no runs exist.
    """

    return average_metric(runs, value_getter=lambda run: run.coins_per_hour)


def average_metric(
    runs: Iterable[RunAnalysis],
    *,
    value_getter: Callable[[RunAnalysis], float | None],
) -> float | None:
    """Compute an average across runs for a selected metric.

    Args:
        runs: Per-run analysis results.
        value_getter: Callable that extracts a float value from a run.

    Returns:
        Arithmetic mean across extracted values, or None when no values exist.
    """

    total = 0.0
    count = 0
    for run in runs:
        value = value_getter(run)
        if value is None:
            continue
        total += value
        count += 1
    if count == 0:
        return None
    return total / count


def summarize_window(
    runs: Iterable[RunAnalysis],
    *,
    start_date: date,
    end_date: date,
) -> WindowSummary:
    """Summarize coins/hour metrics for a date window.

    Args:
        runs: Per-run analysis results.
        start_date: Window start date (inclusive).
        end_date: Window end date (inclusive).

    Returns:
        WindowSummary including run count and average coins/hour.
    """

    window_runs = filter_runs_by_date(runs, start_date=start_date, end_date=end_date)
    return WindowSummary(
        start_date=start_date,
        end_date=end_date,
        run_count=len(window_runs),
        average_coins_per_hour=average_coins_per_hour(window_runs),
    )


def daily_average_series(
    runs: Iterable[RunAnalysis],
    *,
    value_getter: Callable[[RunAnalysis], float | None] | None = None,
) -> dict[str, float]:
    """Aggregate runs into a daily average series keyed by ISO date.

    Args:
        runs: Per-run analysis results.
        value_getter: Optional callable extracting the metric value from a run.
            Defaults to `run.coins_per_hour`.

    Returns:
        Mapping of `YYYY-MM-DD` -> average metric value for that day.
    """

    if value_getter is None:
        value_getter = lambda run: run.coins_per_hour

    buckets: dict[str, list[float]] = defaultdict(list)
    for run in runs:
        value = value_getter(run)
        if value is None:
            continue
        key = run.battle_date.date().isoformat()
        buckets[key].append(value)

    averaged: dict[str, float] = {}
    for key, values in buckets.items():
        averaged[key] = sum(values) / len(values)
    return dict(sorted(averaged.items(), key=lambda kv: kv[0]))


def simple_moving_average(
    values: Sequence[float | None],
    *,
    window: int,
) -> list[float | None]:
    """Compute a simple moving average over a numeric series.

    Args:
        values: A sequence of values aligned to chart labels (None for missing).
        window: Window size (>= 2).

    Returns:
        A list the same length as `values`, with None for indices that cannot be
        computed due to insufficient history or missing inputs.
    """

    if window < 2:
        raise ValueError("window must be >= 2")

    averaged: list[float | None] = [None] * len(values)
    for idx in range(window - 1, len(values)):
        window_values = values[idx - window + 1 : idx + 1]
        if any(v is None for v in window_values):
            continue
        averaged[idx] = sum(v for v in window_values if v is not None) / window
    return averaged
