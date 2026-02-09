"""Chart execution for Phase 7 ChartConfigDTO.

This module consumes ChartConfigDTO and produces deterministic DTO outputs that
the UI can render without performing calculations inline.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from analysis.aggregations import simple_moving_average
from analysis.chart_config_dto import ChartConfigDTO
from analysis.dto import MetricPoint
from analysis.engine import analyze_metric_series
from analysis.series_registry import MetricSeriesRegistry


@dataclass(frozen=True, slots=True)
class ChartDatasetDTO:
    """A chart dataset produced from a ChartConfigDTO.

    Args:
        label: Dataset label shown in legends.
        metric_key: MetricSeries key used for the dataset.
        unit: Display unit string.
        values: Values aligned to `ChartDataDTO.labels` or metric-vs-metric points.
        run_counts: Count of non-null contributing points aligned to labels.
        scope_label: Optional scope label when produced from a two-scope comparison.
    """

    label: str
    metric_key: str
    unit: str
    values: list[float | None] | list[dict[str, float | int | None]]
    run_counts: list[int]
    scope_label: str | None = None


@dataclass(frozen=True, slots=True)
class ChartDataDTO:
    """Chart output DTO produced from a ChartConfigDTO.

    Args:
        labels: ISO date labels for time-based charts.
        datasets: Datasets aligned to labels or metric-vs-metric points.
        chart_type: Config chart type (line/bar/area/scatter/donut).
        x_axis: X-axis mode ("time" or "metric").
        x_label: X-axis label for metric-vs-metric charts.
        x_unit: X-axis unit for metric-vs-metric charts.
        y_label: Y-axis label for metric-vs-metric charts.
        y_unit: Y-axis unit for metric-vs-metric charts.
        run_ids: Run id list aligned to metric-vs-metric points.
    """

    labels: list[str]
    datasets: list[ChartDatasetDTO]
    chart_type: str
    x_axis: str = "time"
    x_label: str | None = None
    x_unit: str | None = None
    y_label: str | None = None
    y_unit: str | None = None
    run_ids: list[int | None] | None = None


def analyze_chart_config_dto(
    records: Iterable[object],
    *,
    config: ChartConfigDTO,
    registry: MetricSeriesRegistry,
    moving_average_window: int | None,
    entity_selections: dict[str, str | None],
) -> ChartDataDTO:
    """Analyze a ChartConfigDTO into chart-ready datasets.

    Args:
        records: Iterable/QuerySet of battle report records already filtered by context.
        config: ChartConfigDTO to execute.
        registry: MetricSeriesRegistry for labels/units and aggregation semantics.
        moving_average_window: Optional rolling window for smoothing.
        entity_selections: Mapping for entity selections (unused for Phase 7 builder config).

    Returns:
        ChartDataDTO suitable for conversion into Chart.js data.
    """

    _ = entity_selections

    if config.chart_type == "donut":
        return _analyze_donut(records, config=config, registry=registry)
    if config.x_axis == "metric":
        return _analyze_metric_axis(records, config=config, registry=registry)

    metric_points_by_key: dict[str, tuple[MetricPoint, ...]] = {}
    for metric_key in config.metrics:
        result = analyze_metric_series(
            records,
            metric_key=metric_key,
            transform="none",
            context=None,
            entity_type=None,
            entity_name=None,
        )
        metric_points_by_key[metric_key] = result.points

    labels = sorted({point.battle_date.date().isoformat() for points in metric_points_by_key.values() for point in points})
    datasets: list[ChartDatasetDTO] = []
    for metric_key in config.metrics:
        spec = registry.get(metric_key)
        if spec is None:
            continue
        groups = _group_points(metric_points_by_key[metric_key], config=config)
        for group_label, points in groups.items():
            aggregation = config.aggregation or spec.aggregation
            values, counts = _aggregate_points(points, labels, aggregation=aggregation)
            if config.smoothing == "rolling_avg":
                window = moving_average_window or 7
                values = [round(v, 2) if v is not None else None for v in simple_moving_average(values, window=window)]
            label = spec.label if group_label == "all" else f"{group_label} • {spec.label}"
            datasets.append(
                ChartDatasetDTO(
                    label=label,
                    metric_key=metric_key,
                    unit=spec.unit,
                    values=values,
                    run_counts=counts,
                    scope_label=(None if group_label == "all" else group_label),
                )
            )

    return ChartDataDTO(labels=labels, datasets=datasets, chart_type=config.chart_type)


def _analyze_metric_axis(
    records: Iterable[object],
    *,
    config: ChartConfigDTO,
    registry: MetricSeriesRegistry,
) -> ChartDataDTO:
    """Analyze a metric-vs-metric chart configuration into point datasets.

    Args:
        records: Iterable/QuerySet of battle report records already filtered by context.
        config: ChartConfigDTO to execute (metric-vs-metric mode).
        registry: MetricSeriesRegistry for labels/units.

    Returns:
        ChartDataDTO with x/y labels and point datasets.
    """

    if len(config.metrics) < 2:
        return ChartDataDTO(labels=[], datasets=[], chart_type=config.chart_type, x_axis="metric")

    x_key = config.metrics[0]
    y_key = config.metrics[1]
    x_spec = registry.get(x_key)
    y_spec = registry.get(y_key)
    if x_spec is None or y_spec is None:
        return ChartDataDTO(labels=[], datasets=[], chart_type=config.chart_type, x_axis="metric")

    x_result = analyze_metric_series(
        records,
        metric_key=x_key,
        transform="none",
        context=None,
        entity_type=None,
        entity_name=None,
    )
    y_result = analyze_metric_series(
        records,
        metric_key=y_key,
        transform="none",
        context=None,
        entity_type=None,
        entity_name=None,
    )

    points: list[dict[str, float | int | None]] = []
    run_ids: list[int | None] = []
    for x_point, y_point in zip(x_result.points, y_result.points, strict=False):
        if x_point.value is None or y_point.value is None:
            continue
        run_id = x_point.run_id if x_point.run_id is not None else y_point.run_id
        points.append({"x": float(x_point.value), "y": float(y_point.value), "runId": run_id})
        run_ids.append(run_id)

    label = f"{y_spec.label} vs {x_spec.label}"
    datasets = [
        ChartDatasetDTO(
            label=label,
            metric_key=y_key,
            unit=y_spec.unit,
            values=points,
            run_counts=[],
        )
    ]
    return ChartDataDTO(
        labels=[],
        datasets=datasets,
        chart_type=config.chart_type,
        x_axis="metric",
        x_label=x_spec.label,
        x_unit=x_spec.unit,
        y_label=y_spec.label,
        y_unit=y_spec.unit,
        run_ids=run_ids,
    )


def _analyze_donut(records: Iterable[object], *, config: ChartConfigDTO, registry: MetricSeriesRegistry) -> ChartDataDTO:
    """Analyze a donut chart by aggregating selected metrics across records."""

    has_any = _iterable_has_any(records)
    labels: list[str] = []
    datasets: list[ChartDatasetDTO] = []
    values: list[float | None] = []
    counts: list[int] = []
    units: list[str] = []

    for metric_key in config.metrics:
        spec = registry.get(metric_key)
        if spec is None:
            continue
        labels.append(spec.label)
        units.append(spec.unit)
        if not has_any:
            values.append(None)
            counts.append(0)
            continue
        result = analyze_metric_series(
            records,
            metric_key=metric_key,
            transform="none",
            context=None,
            entity_type=None,
            entity_name=None,
        )
        total = 0.0
        count = 0
        for point in result.points:
            if point.value is None:
                continue
            total += float(point.value)
            count += 1
        aggregation = config.aggregation or spec.aggregation
        if aggregation == "avg" and count:
            values.append(round(total / count, 2))
        else:
            values.append(round(total, 2))
        counts.append(count)

    unit = units[0] if units and all(u == units[0] for u in units) else ""
    datasets.append(
        ChartDatasetDTO(
            label="Donut",
            metric_key="donut",
            unit=unit,
            values=values,
            run_counts=counts,
        )
    )
    return ChartDataDTO(labels=labels, datasets=datasets, chart_type="donut")


def _iterable_has_any(records: Iterable[object]) -> bool:
    """Return True when an iterable contains at least one record."""

    exists = getattr(records, "exists", None)
    if callable(exists):
        return bool(exists())
    try:
        return len(records) > 0  # type: ignore[arg-type]
    except TypeError:
        return any(True for _ in records)


def _group_points(points: tuple[MetricPoint, ...], *, config: ChartConfigDTO) -> dict[str, list[MetricPoint]]:
    """Group points according to config grouping/comparison settings."""

    if config.comparison != "none" and config.scopes and len(config.scopes) == 2:
        a, b = config.scopes
        grouped: dict[str, list[MetricPoint]] = {a.label: [], b.label: []}
        for point in points:
            if config.comparison == "run_vs_run":
                if point.run_id == a.run_id:
                    grouped[a.label].append(point)
                elif point.run_id == b.run_id:
                    grouped[b.label].append(point)
                continue
            point_date = point.battle_date.date()
            if a.start_date and a.end_date and a.start_date <= point_date <= a.end_date:
                grouped[a.label].append(point)
            elif b.start_date and b.end_date and b.start_date <= point_date <= b.end_date:
                grouped[b.label].append(point)
        return grouped

    if config.group_by == "tier":
        groups: dict[str, list[MetricPoint]] = {}
        for point in points:
            if point.tier is None:
                continue
            groups.setdefault(f"Tier {point.tier}", []).append(point)
        return groups or {"all": list(points)}

    if config.group_by == "preset":
        groups = {}
        for point in points:
            key = point.preset_name or "No preset"
            groups.setdefault(str(key), []).append(point)
        return groups or {"all": list(points)}

    return {"all": list(points)}


def _aggregate_points(
    points: list[MetricPoint],
    labels: list[str],
    *,
    aggregation: str,
) -> tuple[list[float | None], list[int]]:
    """Aggregate points into daily series aligned to label dates."""

    buckets: dict[str, list[float]] = {}
    for point in points:
        if point.value is None:
            continue
        key = point.battle_date.date().isoformat()
        buckets.setdefault(key, []).append(point.value)

    by_date: dict[str, float] = {}
    counts: dict[str, int] = {}
    for key, values in buckets.items():
        counts[key] = len(values)
        if aggregation == "sum":
            by_date[key] = sum(values)
        else:
            by_date[key] = sum(values) / len(values)

    series = [by_date.get(label) for label in labels]
    series_counts = [counts.get(label, 0) for label in labels]
    return series, series_counts
