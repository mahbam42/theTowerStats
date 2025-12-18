"""Generic rendering for ChartConfig-driven Chart.js datasets."""

from __future__ import annotations

import json
from dataclasses import dataclass
from dataclasses import asdict
from datetime import date
from hashlib import sha256
from typing import TypedDict

from analysis.aggregations import simple_moving_average
from analysis.derived_formula import evaluate_formula
from analysis.dto import MetricPoint
from analysis.engine import analyze_metric_series
from collections.abc import Iterable

from analysis.series_registry import MetricSeriesRegistry

from .schema import ChartConfig, ChartSeriesConfig
from .flags import INCOMPLETE_RUN, PATCH_BOUNDARY, ROLLING_MEDIAN_DEVIATION, apply_patch_boundaries, rolling_median_flags


class ChartDataset(TypedDict, total=False):
    """A Chart.js dataset payload for the dashboard."""

    label: str
    metricKey: str
    metricKind: str
    unit: str
    seriesKind: str
    data: list[float | None]
    borderColor: str
    backgroundColor: str | list[str]
    spanGaps: bool
    borderDash: list[int]
    borderWidth: int
    pointRadius: int | list[int]
    pointHoverRadius: int | list[int]
    pointBackgroundColor: str | list[str]
    tension: float
    flagReasons: list[str | None]


class ChartData(TypedDict):
    """The full Chart.js payload (labels + datasets) for a chart panel."""

    labels: list[str]
    datasets: list[ChartDataset]


@dataclass(frozen=True, slots=True)
class RenderedChart:
    """A rendered chart panel produced from a ChartConfig."""

    config: ChartConfig
    data: ChartData
    unit: str
    error: str | None = None
    warnings: tuple[str, ...] = ()


MAX_CHART_LABELS = 400


def render_charts(
    *,
    configs: tuple[ChartConfig, ...],
    records: Iterable[object],
    registry: MetricSeriesRegistry,
    moving_average_window: int | None,
    entity_selections: dict[str, str | None],
    patch_boundaries: tuple[date, ...] = (),
) -> tuple[RenderedChart, ...]:
    """Render a set of charts from configs and already-filtered records.

    Args:
        configs: ChartConfig entries to render.
        records: Iterable/QuerySet of run records (already filtered by date/tier/preset).
        registry: MetricSeriesRegistry for metric capabilities and labels.
        moving_average_window: Optional window size for moving average transforms.
        entity_selections: Mapping for entity filters ("uw", "guardian", "bot") to selected names.

    Returns:
        RenderedChart entries in the same order as `configs`.
    """

    rendered: list[RenderedChart] = []
    cache: dict[str, RenderedChart] = {}
    for config in configs:
        cache_key = _chart_cache_key(
            config=config,
            entity_selections=entity_selections,
            moving_average_window=moving_average_window,
            patch_boundaries=patch_boundaries,
        )
        if cache_key not in cache:
            cache[cache_key] = render_chart(
                config=config,
                records=records,
                registry=registry,
                moving_average_window=moving_average_window,
                entity_selections=entity_selections,
                patch_boundaries=patch_boundaries,
            )
        rendered.append(cache[cache_key])
    return tuple(rendered)


def render_chart(
    *,
    config: ChartConfig,
    records: Iterable[object],
    registry: MetricSeriesRegistry,
    moving_average_window: int | None,
    entity_selections: dict[str, str | None],
    patch_boundaries: tuple[date, ...] = (),
) -> RenderedChart:
    """Render a single chart panel from a ChartConfig.

    Args:
        config: ChartConfig to render.
        records: Iterable/QuerySet of run records (already filtered by date/tier/preset).
        registry: MetricSeriesRegistry for labels/units and supported transforms.
        moving_average_window: Optional window size for moving average transforms.
        entity_selections: Mapping for entity filters ("uw", "guardian", "bot") to selected names.

    Returns:
        RenderedChart containing chart labels and datasets.
    """

    if config.chart_type == "donut":
        return _render_donut_chart(
            config=config,
            records=records,
            registry=registry,
            entity_selections=entity_selections,
        )

    if config.derived is not None:
        derived_points = _compute_derived_points(
            config=config,
            records=records,
            moving_average_window=moving_average_window,
            entity_selections=entity_selections,
        )
        derived_labels = sorted({point.battle_date.date().isoformat() for point in derived_points})
        derived_series = _aggregate_points(derived_points, derived_labels, aggregation="avg")
        unit = _infer_division_unit(config=config, registry=registry) or "derived"
        derived_datasets = [
            _dataset(
                label=config.title,
                metric_key=config.id,
                metric_kind="derived",
                unit=unit,
                data=derived_series,
                color="#3366CC",
            )
        ]
        return RenderedChart(
            config=config,
            data={"labels": derived_labels, "datasets": derived_datasets},
            unit=unit,
        )

    datasets: list[ChartDataset] = []
    labels: list[str] = []
    warnings: list[str] = []
    incomplete_labels = _incomplete_run_labels(records)
    for series_config in config.metric_series:
        spec = registry.get(series_config.metric_key)
        if spec is None:
            continue

        entity_type, entity_name = _entity_scope_for_series(config, entity_selections)
        series_result = analyze_metric_series(
            records,
            metric_key=series_config.metric_key,
            transform=_engine_transform(series_config),
            context=None,
            entity_type=entity_type,
            entity_name=entity_name,
        )
        groups = _group_points(series_result.points, config=config)
        labels = _merge_labels(labels, [p.battle_date.date().isoformat() for p in series_result.points])
        if len(labels) > MAX_CHART_LABELS:
            return RenderedChart(
                config=config,
                data={"labels": [], "datasets": []},
                unit="",
                error=f"Too many data points to render safely (>{MAX_CHART_LABELS}). Narrow the date range or rolling window.",
            )

        unit = _unit_for_series(spec.unit, series_config)
        for group_key, points in groups.items():
            group_label = _label_for_group(group_key, config=config)
            color = _color_for_group(group_key, config=config)
            aggregation = "avg" if series_config.transform == "rate_per_hour" else spec.aggregation
            data = _aggregate_points(points, labels, aggregation=aggregation)
            data = _apply_series_transform(
                data,
                series_config=series_config,
                moving_average_window=moving_average_window,
            )
            label = _series_label(config=config, series=series_config, group_label=group_label, spec_label=spec.label)
            dataset = _dataset(
                label=label,
                metric_key=series_config.metric_key,
                metric_kind=spec.kind,
                unit=unit,
                data=data,
                color=color,
                series_kind=series_config.transform,
            )
            if series_config.transform in ("none", "rate_per_hour"):
                reasons = _flag_reasons(
                    labels,
                    data=data,
                    incomplete_labels=incomplete_labels,
                    patch_boundaries=patch_boundaries,
                )
                if any(reasons):
                    dataset["flagReasons"] = reasons
                    dataset["pointRadius"] = [6 if r else 2 for r in reasons]
                    dataset["pointHoverRadius"] = [8 if r else 5 for r in reasons]
                    dataset["pointBackgroundColor"] = ["#DC3912" if r else color for r in reasons]
            datasets.append(dataset)

        if config.comparison is not None and config.comparison.mode in ("before_after", "run_vs_run"):
            sizes = {k: len(v) for k, v in groups.items() if k != "all"}
            if sizes and any(count < 3 for count in sizes.values()):
                warnings.append("Comparison scope contains fewer than 3 runs; interpret deltas cautiously.")

    panel_unit = datasets[0]["unit"] if datasets else ""
    return RenderedChart(
        config=config,
        data={"labels": labels, "datasets": datasets},
        unit=panel_unit,
        warnings=tuple(warnings),
    )


def _chart_cache_key(
    *,
    config: ChartConfig,
    entity_selections: dict[str, str | None],
    moving_average_window: int | None,
    patch_boundaries: tuple[date, ...],
) -> str:
    """Return a content-based cache key for chart rendering.

    Notes:
        This cache is request-local and is intended as a small guardrail against
        redundant work when the same config is rendered multiple times.
    """

    payload = {
        "config": _jsonable_config(config),
        "entity_selections": entity_selections,
        "moving_average_window": moving_average_window,
        "patch_boundaries": [d.isoformat() for d in patch_boundaries],
    }
    dumped = json.dumps(payload, sort_keys=True, default=str)
    return sha256(dumped.encode("utf-8")).hexdigest()


def _jsonable_config(config: ChartConfig) -> dict[str, object]:
    """Convert a ChartConfig dataclass into a JSON-serializable dictionary."""

    raw = asdict(config)
    raw_filters = raw.get("filters") or {}
    date_range = raw_filters.get("date_range") or {}
    default_start = date_range.get("default_start")
    if default_start is not None:
        date_range["default_start"] = str(default_start)
        raw_filters["date_range"] = date_range
        raw["filters"] = raw_filters
    return raw


def _render_donut_chart(
    *,
    config: ChartConfig,
    records: Iterable[object],
    registry: MetricSeriesRegistry,
    entity_selections: dict[str, str | None],
) -> RenderedChart:
    """Render a donut chart by aggregating selected metrics across filtered runs.

    Args:
        config: ChartConfig with `chart_type="donut"`.
        records: Iterable/QuerySet of run records (already filtered by context).
        registry: MetricSeriesRegistry for labels/units.
        entity_selections: Mapping for entity filters ("uw", "guardian", "bot") to selected names.

    Returns:
        RenderedChart with labels representing slices and a single dataset.
    """

    has_any_records = _iterable_has_any(records)

    slice_labels: list[str] = []
    slice_values: list[float | None] = []
    slice_units: list[str] = []
    slice_colors: list[str] = []

    palette = [
        "#3366CC",
        "#DC3912",
        "#FF9900",
        "#109618",
        "#990099",
        "#0099C6",
        "#DD4477",
        "#66AA00",
        "#B82E2E",
        "#316395",
        "#994499",
        "#22AA99",
    ]

    for idx, series_config in enumerate(config.metric_series):
        spec = registry.get(series_config.metric_key)
        if spec is None:
            continue

        slice_label = series_config.label or spec.label
        slice_labels.append(slice_label)
        slice_units.append(_unit_for_series(spec.unit, series_config))
        if not has_any_records:
            slice_values.append(None)
        else:
            entity_type, entity_name = _entity_scope_for_series(config, entity_selections)
            series_result = analyze_metric_series(
                records,
                metric_key=series_config.metric_key,
                transform=_engine_transform(series_config),
                context=None,
                entity_type=entity_type,
                entity_name=entity_name,
            )
            total = 0.0
            for point in series_result.points:
                if point.value is None:
                    continue
                total += float(point.value)
            slice_values.append(round(total, 2))
        slice_colors.append(palette[idx % len(palette)])

    unit = slice_units[0] if slice_units and all(u == slice_units[0] for u in slice_units) else ""
    dataset: ChartDataset = {
        "label": config.title,
        "metricKey": config.id,
        "metricKind": "observed",
        "unit": unit,
        "seriesKind": "donut",
        "data": slice_values,
        "borderColor": "#ffffff",
        "backgroundColor": slice_colors,
    }
    return RenderedChart(config=config, data={"labels": slice_labels, "datasets": [dataset]}, unit=unit)


def _iterable_has_any(records: Iterable[object]) -> bool:
    """Return True when an iterable contains at least one record.

    Args:
        records: Records iterable, typically a Django QuerySet.

    Returns:
        True when at least one record is present; otherwise False.
    """

    exists = getattr(records, "exists", None)
    if callable(exists):
        return bool(exists())

    try:
        return len(records) > 0  # type: ignore[arg-type]
    except TypeError:
        return any(True for _ in records)


def _engine_transform(series: ChartSeriesConfig) -> str:
    """Translate a chart-series transform into an engine transform."""

    return "rate_per_hour" if series.transform == "rate_per_hour" else "none"


def _apply_series_transform(
    data: list[float | None],
    *,
    series_config: ChartSeriesConfig,
    moving_average_window: int | None,
) -> list[float | None]:
    """Apply chart-side transforms to an already-aggregated data list."""

    if series_config.transform == "moving_average":
        window = moving_average_window or 7
        return [round(v, 2) if v is not None else None for v in simple_moving_average(data, window=window)]

    if series_config.transform == "cumulative":
        running = 0.0
        out: list[float | None] = []
        for value in data:
            if value is None:
                out.append(None)
                continue
            running += value
            out.append(round(running, 2))
        return out

    return [round(v, 2) if v is not None else None for v in data]


def _incomplete_run_labels(records: Iterable[object]) -> set[str]:
    """Return ISO date labels that contain at least one incomplete run.

    Args:
        records: Typically a BattleReport QuerySet filtered to the current context.

    Returns:
        Set of ISO date strings ("YYYY-MM-DD") where a run is missing key metadata.
    """

    labels: set[str] = set()
    for record in records:
        progress = getattr(record, "run_progress", None)
        battle_date = getattr(progress, "battle_date", None)
        if battle_date is None:
            continue
        wave = getattr(progress, "wave", None)
        real_time = getattr(progress, "real_time_seconds", None)
        if wave is None or real_time is None:
            labels.add(battle_date.date().isoformat())
    return labels


def _flag_reasons(
    labels: list[str],
    *,
    data: list[float | None],
    incomplete_labels: set[str],
    patch_boundaries: tuple[date, ...],
) -> list[str | None]:
    """Compute per-point flag reasons aligned to labels.

    Args:
        labels: ISO date labels for the series.
        data: Series values aligned to labels.
        incomplete_labels: Set of labels containing incomplete run metadata.
        patch_boundaries: Known boundary dates (best-effort, optional).

    Returns:
        List of optional reason strings aligned to `labels`.
    """

    reasons: list[list[str]] = [[] for _ in labels]

    for idx, label in enumerate(labels):
        if label in incomplete_labels:
            reasons[idx].append(INCOMPLETE_RUN.description)

    for idx, flagged in enumerate(rolling_median_flags(data, window=7)):
        if flagged:
            reasons[idx].append(ROLLING_MEDIAN_DEVIATION.description)

    for idx, flagged in enumerate(apply_patch_boundaries(labels, boundary_dates=patch_boundaries)):
        if flagged:
            reasons[idx].append(PATCH_BOUNDARY.description)

    return ["; ".join(items) if items else None for items in reasons]

def _aggregate_points(points: list[MetricPoint], labels: list[str], *, aggregation: str) -> list[float | None]:
    """Aggregate run points into daily series aligned to label dates."""

    buckets: dict[str, list[float]] = {}
    for point in points:
        if point.value is None:
            continue
        key = point.battle_date.date().isoformat()
        buckets.setdefault(key, []).append(point.value)

    by_date: dict[str, float] = {}
    for key, values in buckets.items():
        if aggregation == "sum":
            by_date[key] = sum(values)
        else:
            by_date[key] = sum(values) / len(values)

    return [by_date.get(label) for label in labels]


def _group_points(points: tuple[MetricPoint, ...], *, config: ChartConfig) -> dict[object, list[MetricPoint]]:
    """Group points according to chart comparison mode."""

    if config.comparison is None or config.comparison.mode == "none":
        return {"all": list(points)}

    mode = config.comparison.mode
    if mode in ("before_after", "run_vs_run"):
        scopes = config.comparison.scopes or ()
        if len(scopes) != 2:
            return {"all": list(points)}
        grouped: dict[object, list[MetricPoint]] = {scopes[0].label: [], scopes[1].label: []}
        for point in points:
            if mode == "run_vs_run":
                if point.run_id == scopes[0].run_id:
                    grouped[scopes[0].label].append(point)
                elif point.run_id == scopes[1].run_id:
                    grouped[scopes[1].label].append(point)
                continue

            point_date = point.battle_date.date()
            a = scopes[0]
            b = scopes[1]
            if a.start_date and a.end_date and a.start_date <= point_date <= a.end_date:
                grouped[a.label].append(point)
            elif b.start_date and b.end_date and b.start_date <= point_date <= b.end_date:
                grouped[b.label].append(point)

        if any(grouped.values()):
            return grouped
        return {"all": list(points)}

    if mode == "by_tier":
        groups: dict[object, list[MetricPoint]] = {}
        for point in points:
            if point.tier is None:
                continue
            groups.setdefault(point.tier, []).append(point)
        return groups or {"all": list(points)}

    if mode == "by_preset":
        groups = {}
        for point in points:
            key = point.preset_name or "No preset"
            groups.setdefault(key, []).append(point)
        return groups or {"all": list(points)}

    return {"all": list(points)}


def _series_label(
    *,
    config: ChartConfig,
    series: ChartSeriesConfig,
    group_label: str | None,
    spec_label: str,
) -> str:
    """Build a dataset label for a chart series."""

    if group_label and len(config.metric_series) == 1 and series.label is None:
        return group_label

    base = series.label or (config.title if len(config.metric_series) == 1 else spec_label)
    if group_label:
        return f"{group_label} • {base}"
    return base


def _merge_labels(existing: list[str], new_labels: list[str]) -> list[str]:
    """Merge ISO date labels into a sorted unique list."""

    merged = sorted(set(existing).union(new_labels))
    return merged


def _unit_for_series(base_unit: str, series: ChartSeriesConfig) -> str:
    """Return the displayed unit for a series after transforms."""

    if series.transform == "rate_per_hour":
        return f"{base_unit}/hour"
    return base_unit


def _dataset(
    *,
    label: str,
    metric_key: str,
    metric_kind: str,
    unit: str,
    data: list[float | None],
    color: str,
    series_kind: str = "raw",
) -> ChartDataset:
    """Build a Chart.js dataset dict with consistent styling."""

    dataset: ChartDataset = {
        "label": label,
        "metricKey": metric_key,
        "metricKind": metric_kind,
        "unit": unit,
        "seriesKind": series_kind,
        "data": data,
        "borderColor": color,
        "backgroundColor": color,
        "spanGaps": False,
        "borderWidth": 2,
        "pointRadius": 2,
        "pointHoverRadius": 5,
        "tension": 0.15,
    }
    if series_kind in ("moving_average", "cumulative"):
        dataset["borderDash"] = [6, 4]
        dataset["pointRadius"] = 0
        dataset["pointHoverRadius"] = 3
    return dataset


def _label_for_group(key: object, *, config: ChartConfig) -> str | None:
    """Return a human-friendly label for a grouping key."""

    if config.comparison is None or config.comparison.mode == "none":
        return None
    if config.comparison.mode == "by_tier":
        return f"Tier {key}"
    if config.comparison.mode == "by_preset":
        return str(key)
    return str(key)


def _color_for_group(key: object, *, config: ChartConfig) -> str:
    """Return a stable dataset color based on the group key."""

    if config.comparison is None or config.comparison.mode == "none":
        return "#3366CC"
    if config.comparison.mode == "by_tier":
        return _color_for_tier(key)
    if config.comparison.mode == "by_preset":
        return _color_for_preset(key)
    if config.comparison.mode in ("before_after", "run_vs_run"):
        scopes = config.comparison.scopes or ()
        if len(scopes) == 2 and str(key) == scopes[0].label:
            return "#3366CC"
        return "#FF9900"
    return "#777777"


def _color_for_tier(tier: object) -> str:
    """Return a stable color for a tier number."""

    palette = [
        "#3366CC",
        "#DC3912",
        "#FF9900",
        "#109618",
        "#990099",
        "#0099C6",
        "#DD4477",
        "#66AA00",
        "#B82E2E",
        "#316395",
    ]
    if isinstance(tier, int) and tier >= 1:
        return palette[(tier - 1) % len(palette)]
    return "#777777"


def _color_for_preset(preset_name: object) -> str:
    """Return a stable color for preset labels."""

    name = str(preset_name) if preset_name is not None else ""
    hashed = sum(ord(c) for c in name) % 360
    return f"hsl({hashed}, 65%, 45%)"


def _entity_scope_for_series(
    config: ChartConfig,
    entity_selections: dict[str, str | None],
) -> tuple[str | None, str | None]:
    """Return analysis-engine entity scope inferred from enabled chart filters."""

    if config.filters.uw.enabled:
        return "ultimate_weapon", entity_selections.get("uw")
    if config.filters.guardian.enabled:
        return "guardian_chip", entity_selections.get("guardian")
    if config.filters.bot.enabled:
        return "bot", entity_selections.get("bot")
    return None, None


def _compute_derived_points(
    *,
    config: ChartConfig,
    records: Iterable[object],
    moving_average_window: int | None,
    entity_selections: dict[str, str | None],
) -> list[MetricPoint]:
    """Compute per-run derived points for a derived ChartConfig."""

    _ = moving_average_window

    by_key: dict[str, dict[int | None, MetricPoint]] = {}
    for series in config.metric_series:
        entity_type, entity_name = _entity_scope_for_series(config, entity_selections)
        result = analyze_metric_series(
            records,
            metric_key=series.metric_key,
            transform=_engine_transform(series),
            context=None,
            entity_type=entity_type,
            entity_name=entity_name,
        )
        by_key[series.metric_key] = {point.run_id: point for point in result.points}

    derived_points: list[MetricPoint] = []
    run_ids = set.intersection(*(set(mapping.keys()) for mapping in by_key.values())) if by_key else set()
    for run_id in run_ids:
        sample = next(iter(by_key.values())).get(run_id)
        if sample is None:
            continue
        variables = {key: by_key[key][run_id].value for key in by_key}
        value = evaluate_formula(config.derived.formula, variables) if config.derived is not None else None
        derived_points.append(
            MetricPoint(
                run_id=run_id,
                battle_date=sample.battle_date,
                tier=sample.tier,
                preset_name=sample.preset_name,
                value=value,
            )
        )

    derived_points.sort(key=lambda p: p.battle_date)
    return derived_points


def _infer_division_unit(*, config: ChartConfig, registry: MetricSeriesRegistry) -> str | None:
    """Infer a unit string for simple a/b formulas when possible."""

    if config.derived is None:
        return None
    formula = config.derived.formula.replace(" ", "")
    if "/" not in formula:
        return None
    left, right = formula.split("/", 1)
    left_spec = registry.get(left)
    right_spec = registry.get(right)
    if left_spec is None or right_spec is None:
        return None
    return f"{left_spec.unit}/{right_spec.unit}"
