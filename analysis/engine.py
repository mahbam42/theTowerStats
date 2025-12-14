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
from .quantity import UnitType, parse_quantity
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

        run_id = _coerce_int(getattr(progress, "id", None))
        if run_id is None:
            run_id = _coerce_int(getattr(record, "id", None))

        battle_date = _coerce_datetime(
            getattr(progress, "battle_date", None) or getattr(record, "parsed_at", None)
        )
        tier = _coerce_int(getattr(progress, "tier", None))
        preset_name = _preset_name_from_progress(progress)
        coins = _coerce_int(getattr(progress, "coins", None))
        if coins is None:
            coins = _coins_from_raw_text(getattr(record, "raw_text", None))
        real_time_seconds = _coerce_int(getattr(progress, "real_time_seconds", None))
        if battle_date is None or coins is None or real_time_seconds is None:
            continue

        metric = coins_per_hour(coins=coins, real_time_seconds=real_time_seconds)
        if metric is None:
            continue

        runs.append(
            RunAnalysis(
                run_id=run_id,
                battle_date=battle_date,
                tier=tier,
                preset_name=preset_name,
                coins_per_hour=metric,
            )
        )

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


def _coerce_datetime(value: object) -> datetime | None:
    """Coerce an object into a datetime when safe."""

    if isinstance(value, datetime):
        return value
    return None


def _preset_name_from_progress(progress: object) -> str | None:
    """Extract an optional preset name from a run-progress-like object."""

    preset_obj = getattr(progress, "preset_tag", None)
    preset_name = getattr(preset_obj, "name", None)
    if isinstance(preset_name, str) and preset_name.strip():
        return preset_name.strip()
    return None


_LABEL_SEPARATOR = r"(?:[ \t]*:[ \t]*|\t+[ \t]*|[ \t]{2,})"
_COINS_LINE_RE = re.compile(
    rf"(?im)^[ \t]*(?:Coins|Coins Earned){_LABEL_SEPARATOR}"
    r"([0-9][0-9,]*(?:\.[0-9]+)?[kmbtq]?)\b[ \t]*.*$"
)


def _coins_from_raw_text(raw_text: object) -> int | None:
    """Extract total coins from raw Battle Report text (best-effort)."""

    if not isinstance(raw_text, str):
        return None
    match = _COINS_LINE_RE.search(raw_text)
    if not match:
        return None

    token = match.group(1)
    parsed = parse_quantity(token, unit_type=UnitType.coins)
    if parsed.normalized_value is None or parsed.normalized_value <= 0:
        return None

    try:
        return int(parsed.normalized_value.to_integral_value())
    except (ValueError, OverflowError):
        return None
