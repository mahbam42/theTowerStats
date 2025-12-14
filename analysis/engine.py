"""Orchestration entry points for the Analysis Engine.

The Analysis Engine is a pure, non-Django module that accepts in-memory inputs
and returns DTOs. It must not import Django or perform database writes.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import Protocol, TypeGuard

from .dto import AnalysisResult, RunAnalysis
from .rates import waves_per_hour


class _RunProgressLike(Protocol):
    """Protocol for Phase 1 run-progress inputs (duck-typed)."""

    battle_date: datetime | None
    wave: int | None
    real_time_seconds: int | None


def analyze_runs(records: Iterable[object]) -> AnalysisResult:
    """Analyze runs and return rate metrics (Phase 1).

    Args:
        records: An iterable of `RunProgress`-like objects, or `GameData` objects
            with a `run_progress` attribute.

    Returns:
        AnalysisResult containing a per-run waves-per-hour series.

    Notes:
        Any record missing required fields is skipped. If no records contain the
        required data, an empty result is returned.
    """

    runs: list[RunAnalysis] = []

    for record in records:
        progress = getattr(record, "run_progress", record)
        if not _looks_like_run_progress(progress):
            continue

        battle_date = getattr(progress, "battle_date", None)
        wave = getattr(progress, "wave", None)
        real_time_seconds = getattr(progress, "real_time_seconds", None)
        if battle_date is None or wave is None or real_time_seconds is None:
            continue

        metric = waves_per_hour(wave=wave, real_time_seconds=real_time_seconds)
        if metric is None:
            continue

        runs.append(RunAnalysis(battle_date=battle_date, waves_per_hour=metric))

    runs.sort(key=lambda r: r.battle_date)
    return AnalysisResult(runs=tuple(runs))


def _looks_like_run_progress(obj: object) -> TypeGuard[_RunProgressLike]:
    """Return True if an object exposes the Phase 1 RunProgress interface."""

    return all(hasattr(obj, name) for name in ("battle_date", "wave", "real_time_seconds"))
