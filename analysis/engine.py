"""Orchestration entry points for the Analysis Engine.

The Analysis Engine is a pure, non-Django module that accepts in-memory inputs
and returns DTOs. It must not import Django or perform database writes.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from datetime import datetime
from typing import Protocol, TypeGuard

from .context import PlayerContextInput
from .derived import MonteCarloConfig
from .dto import AnalysisResult, MetricPoint, MetricSeriesResult, RunAnalysis, UsedParameter
from .metrics import MetricComputeConfig, compute_metric_value, get_metric_definition
from .quantity import UnitType
from .units import UnitContract, UnitValidationError, parse_validated_quantity
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


def analyze_metric_series(
    records: Iterable[object],
    *,
    metric_key: str,
    transform: str = "none",
    context: PlayerContextInput | None = None,
    entity_type: str | None = None,
    entity_name: str | None = None,
    monte_carlo_trials: int | None = None,
    monte_carlo_seed: int | None = None,
) -> MetricSeriesResult:
    """Analyze runs for a specific metric, returning a chart-friendly series.

    Args:
        records: An iterable of `RunProgress`-like objects, or `GameData` objects
            with a `run_progress` attribute.
        metric_key: Metric key to compute (observed or derived).
        transform: Optional transform to apply (e.g. "rate_per_hour").
        context: Optional player context + selected parameter tables.
        entity_type: Optional entity category for entity-scoped derived metrics
            (e.g. "ultimate_weapon", "guardian_chip", "bot").
        entity_name: Optional entity name for entity-scoped derived metrics.
        monte_carlo_trials: Optional override for Monte Carlo trial count used by
            simulated EV metrics.
        monte_carlo_seed: Optional override for the Monte Carlo RNG seed.

    Returns:
        MetricSeriesResult with per-run points and transparent metadata about
        used parameters/assumptions.

    Notes:
        Records missing a battle_date are skipped. Other missing fields do not
        raise; values become None instead.
    """

    metric = get_metric_definition(metric_key)
    config = MetricComputeConfig(
        monte_carlo=None
        if monte_carlo_trials is None or monte_carlo_seed is None
        else MonteCarloConfig(trials=monte_carlo_trials, seed=monte_carlo_seed)
    )

    points: list[MetricPoint] = []
    used_parameters: list[UsedParameter] = []
    assumptions: set[str] = set()

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
        cash = _coerce_int(getattr(progress, "cash_earned", None))
        cells = _coerce_int(getattr(progress, "cells_earned", None))
        reroll_shards = _coerce_int(getattr(progress, "reroll_shards_earned", None))
        wave = _coerce_int(getattr(progress, "wave", None))
        real_time_seconds = _coerce_int(getattr(progress, "real_time_seconds", None))
        if battle_date is None:
            continue

        value, used, assumed = compute_metric_value(
            metric.key,
            record=record,
            coins=coins,
            cash=cash,
            cells=cells,
            reroll_shards=reroll_shards,
            wave=wave,
            real_time_seconds=real_time_seconds,
            context=context,
            entity_type=entity_type,
            entity_name=entity_name,
            config=config,
        )

        if transform == "rate_per_hour":
            if value is None or real_time_seconds is None or real_time_seconds <= 0:
                value = None
            else:
                value = value * 3600.0 / real_time_seconds

        used_parameters.extend(used)
        assumptions.update(assumed)
        points.append(
            MetricPoint(
                run_id=run_id,
                battle_date=battle_date,
                tier=tier,
                preset_name=preset_name,
                value=value,
            )
        )

    points.sort(key=lambda p: p.battle_date)
    return MetricSeriesResult(
        metric=metric,
        points=tuple(points),
        used_parameters=tuple(used_parameters),
        assumptions=tuple(sorted(assumptions)),
    )


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

    preset_obj = getattr(progress, "preset_tag", None) or getattr(progress, "preset", None)
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
    try:
        validated = parse_validated_quantity(token, contract=UnitContract(unit_type=UnitType.coins))
    except (UnitValidationError, ValueError):
        return None
    if validated.normalized_value <= 0:
        return None

    try:
        return int(validated.normalized_value.to_integral_value())
    except (ValueError, OverflowError):
        return None
