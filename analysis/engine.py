"""Orchestration entry points for the Analysis Engine.

The Analysis Engine is a pure, non-Django module that accepts in-memory inputs
and returns DTOs. It must not import Django or perform database writes.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from datetime import datetime
from typing import Protocol, TypeGuard

from .dto import AnalysisResult, RunAnalysis
from .rates import coins_per_hour


class _RunProgressLike(Protocol):
    """Protocol for Phase 1 run-progress inputs (duck-typed)."""

    battle_date: datetime | None
    coins: int | None
    wave: int | None
    real_time_seconds: int | None


def analyze_runs(records: Iterable[object]) -> AnalysisResult:
    """Analyze runs and return rate metrics (Phase 1).

    Args:
        records: An iterable of `RunProgress`-like objects, or `GameData` objects
            with a `run_progress` attribute.

    Returns:
        AnalysisResult containing a per-run coins-per-hour series.

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
        coins = _coerce_int(getattr(progress, "coins", None))
        if coins is None:
            coins = _coins_from_raw_text(getattr(record, "raw_text", None))
        real_time_seconds = getattr(progress, "real_time_seconds", None)
        if battle_date is None or coins is None or real_time_seconds is None:
            continue

        metric = coins_per_hour(coins=coins, real_time_seconds=real_time_seconds)
        if metric is None:
            continue

        runs.append(RunAnalysis(battle_date=battle_date, coins_per_hour=metric))

    runs.sort(key=lambda r: r.battle_date)
    return AnalysisResult(runs=tuple(runs))


def _looks_like_run_progress(obj: object) -> TypeGuard[_RunProgressLike]:
    """Return True if an object exposes the Phase 1 RunProgress interface."""

    return all(
        hasattr(obj, name) for name in ("battle_date", "wave", "real_time_seconds")
    )


def _coerce_int(value: object) -> int | None:
    """Coerce an object into an int when safe."""

    if isinstance(value, int):
        return value
    return None


_COINS_RE = re.compile(r"(?im)^[ \t]*Coins[ \t]*:[ \t]*([0-9][0-9,]*)[ \t]*$")


def _coins_from_raw_text(raw_text: object) -> int | None:
    """Extract total coins from raw Battle Report text (best-effort)."""

    if not isinstance(raw_text, str):
        return None
    match = _COINS_RE.search(raw_text)
    if not match:
        return None
    digits = match.group(1).replace(",", "")
    try:
        return int(digits)
    except ValueError:
        return None
