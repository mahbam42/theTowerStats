"""Execution helpers for Explore queries."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from .metrics import MetricComputeConfig, compute_metric_value
from .explore_registry import ExploreBreakdownDefinition, ExploreMetricDefinition, DEFAULT_BREAKDOWNS
from .explore_schema import ExploreQuery


@dataclass(frozen=True, slots=True)
class ExploreResultRow:
    """Aggregated Explore output row."""

    breakdown: tuple[str, ...]
    value: float | None
    sample_count: int
    run_id: int | None


@dataclass(frozen=True, slots=True)
class ExploreExecutionResult:
    """Result of executing an Explore query."""

    rows: tuple[ExploreResultRow, ...]
    run_count: int
    missing_count: int
    total_value: float | None


@dataclass(slots=True)
class _ExploreBucket:
    """Mutable aggregation bucket for Explore execution."""

    value: float
    count: float
    run_id: int | None


def execute_explore_query(
    records: Iterable[object],
    *,
    query: ExploreQuery,
    metric_registry: dict[str, ExploreMetricDefinition],
    breakdown_registry: dict[str, ExploreBreakdownDefinition] | None = None,
) -> ExploreExecutionResult:
    """Execute an Explore query over in-memory records."""

    breakdown_registry = breakdown_registry or DEFAULT_BREAKDOWNS
    breakdowns = tuple(sorted(query.breakdowns, key=lambda entry: entry.order))
    breakdown_defs = [breakdown_registry[entry.dimension] for entry in breakdowns if entry.dimension in breakdown_registry]

    group_breakdowns = [bd for bd in breakdown_defs if bd.kind == "metric_group"]
    group_breakdown = group_breakdowns[0] if group_breakdowns else None
    field_breakdowns = [bd for bd in breakdown_defs if bd.kind == "field"]

    buckets: dict[tuple[str, ...], _ExploreBucket] = {}
    missing_count = 0
    run_count = 0

    metric_key = query.metric.key
    metric_keys = group_breakdown.metric_keys if group_breakdown and group_breakdown.metric_keys else (metric_key,)
    includes_run_breakdown = any(bd.kind == "field" and bd.field == "run" for bd in breakdown_defs)

    for record in records:
        run_count += 1
        field_labels = {
            bd.key: _field_label(record, field=bd.field or bd.key) for bd in field_breakdowns
        }
        run_id = getattr(record, "id", None) if includes_run_breakdown else None

        for current_key in metric_keys:
            value = _metric_value(record, metric_key=current_key)
            if value is None:
                missing_count += 1
                continue

            labels: list[str] = []
            for bd in breakdown_defs:
                if bd.kind == "metric_group":
                    labels.append(_metric_label(metric_registry, key=current_key))
                else:
                    labels.append(field_labels.get(bd.key, "Unknown"))
            bucket_key = tuple(labels) if breakdown_defs else ()
            bucket = buckets.setdefault(bucket_key, _ExploreBucket(value=0.0, count=0.0, run_id=run_id))
            if includes_run_breakdown and bucket.run_id != run_id:
                bucket.run_id = None
            bucket.value += float(value)
            bucket.count += 1.0

    rows: list[ExploreResultRow] = []
    total_sum = 0.0
    total_count = 0.0
    for key, data in buckets.items():
        if query.metric.aggregation == "count":
            value = float(data.count)
        elif query.metric.aggregation == "avg":
            value = float(data.value) / float(data.count) if data.count else None
        else:
            value = float(data.value)
        rows.append(
            ExploreResultRow(
                breakdown=key,
                value=value,
                sample_count=int(data.count),
                run_id=data.run_id,
            )
        )
        total_sum += float(data.value)
        total_count += float(data.count)

    rows.sort(key=lambda row: row.breakdown)
    total_value = None
    if rows:
        if query.metric.aggregation == "avg":
            total_value = (total_sum / total_count) if total_count else None
        else:
            total_value = sum(row.value or 0.0 for row in rows)

    return ExploreExecutionResult(
        rows=tuple(rows),
        run_count=run_count,
        missing_count=missing_count,
        total_value=total_value,
    )


def _field_label(record: object, *, field: str) -> str:
    """Return a human-readable label for a breakdown field."""

    progress = getattr(record, "run_progress", record)
    if field == "run":
        return _run_label(record)
    if field == "tier":
        tier = getattr(progress, "tier", None)
        return f"Tier {tier}" if tier is not None else "Unknown tier"
    if field == "preset":
        preset_name = getattr(progress, "preset_name_snapshot", None)
        if not preset_name:
            preset = getattr(progress, "preset", None)
            preset_name = getattr(preset, "name", None)
        return preset_name or "No preset"
    if field == "tournament_rank":
        is_tournament = bool(getattr(progress, "is_tournament", False))
        rank = getattr(progress, "tournament_rank", None)
        if not is_tournament:
            return "Not tournament"
        return rank.replace("_", " ").title() if rank else "Tournament (unranked)"
    if field == "date":
        battle_date = getattr(record, "effective_battle_date", None)
        if battle_date is None:
            battle_date = getattr(progress, "battle_date", None) or getattr(record, "parsed_at", None)
        if isinstance(battle_date, datetime):
            return battle_date.date().isoformat()
        return "Unknown date"
    if field == "death_cause":
        killed_by = getattr(progress, "killed_by", None)
        if killed_by:
            return str(killed_by)
        return "Not recorded"
    return "Unknown"


def _run_label(record: object) -> str:
    """Format a run label from progress metadata."""

    progress = getattr(record, "run_progress", record)
    battle_date = getattr(progress, "battle_date", None) or getattr(record, "parsed_at", None)
    tier = getattr(progress, "tier", None)
    wave = getattr(progress, "wave", None)
    tier_label = f"T{tier}" if tier is not None else "T?"
    wave_label = f"W{wave}" if wave is not None else "W?"
    if isinstance(battle_date, datetime):
        date_label = battle_date.date().isoformat()
        time_label = battle_date.strftime("%H:%M:%S")
    else:
        date_label = "Unknown date"
        time_label = "Unknown time"
    return f"{tier_label} • {wave_label} • {date_label} {time_label}"


def _metric_label(registry: dict[str, ExploreMetricDefinition], *, key: str) -> str:
    """Return a metric label for a registry key."""

    metric = registry.get(key)
    return metric.label if metric else key


def _metric_value(record: object, *, metric_key: str) -> float | None:
    """Compute a metric value for a record."""

    progress = getattr(record, "run_progress", record)
    coins = getattr(progress, "coins_earned", None)
    cash = getattr(progress, "cash_earned", None)
    interest_earned = getattr(progress, "interest_earned", None)
    cells = getattr(progress, "cells_earned", None)
    reroll_shards = getattr(progress, "reroll_shards_earned", None)
    wave = getattr(progress, "wave", None)
    real_time_seconds = getattr(progress, "real_time_seconds", None)

    value, _used, _assumptions = compute_metric_value(
        metric_key,
        record=record,
        coins=coins,
        cash=cash,
        interest_earned=interest_earned,
        cells=cells,
        reroll_shards=reroll_shards,
        wave=wave,
        real_time_seconds=real_time_seconds,
        context=None,
        entity_type=None,
        entity_name=None,
        config=MetricComputeConfig(monte_carlo=None),
    )
    return value
