"""Schema definitions and validation for Explore queries."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable, Literal

from .explore_registry import (
    DEFAULT_BREAKDOWNS,
    ExploreBreakdownDefinition,
    ExploreMetricDefinition,
    metric_units_for_breakdown,
)

SchemaVersion = Literal["1.0"]
VisualizationHint = Literal["table", "bar", "donut", "kpi"]
FilterOperator = Literal["=", "!=", ">=", "<=", "in", "range"]

SCHEMA_VERSION: SchemaVersion = "1.0"


@dataclass(frozen=True, slots=True)
class ExploreScope:
    """Scope controls for Explore queries."""

    start_date: date | None
    end_date: date | None
    tier: int | None
    preset_id: int | None
    snapshot_id: int | None
    past_n_runs: int | None
    include_hidden: bool = False


@dataclass(frozen=True, slots=True)
class ExploreFilter:
    """A structured filter entry for Explore queries."""

    field: str
    operator: FilterOperator
    value: object | None


@dataclass(frozen=True, slots=True)
class ExploreBreakdown:
    """Breakdown entry for Explore queries."""

    dimension: str
    order: int


@dataclass(frozen=True, slots=True)
class ExploreMetricSelection:
    """Selected metric and aggregation for Explore queries."""

    key: str
    aggregation: Literal["sum", "count", "avg"]
    percent_of_total: bool = False


@dataclass(frozen=True, slots=True)
class ExploreQuery:
    """Explore query schema container."""

    schema_version: str
    player_id: str
    name: str
    scope: ExploreScope
    filters: tuple[ExploreFilter, ...]
    breakdowns: tuple[ExploreBreakdown, ...]
    metrics: tuple[ExploreMetricSelection, ...]
    visualization_hint: VisualizationHint


@dataclass(frozen=True, slots=True)
class ExploreValidationResult:
    """Validation result for Explore queries."""

    errors: tuple[str, ...]
    warnings: tuple[str, ...]

    @property
    def is_valid(self) -> bool:
        """Return True when no validation errors exist."""

        return not self.errors


def validate_explore_query(
    query: ExploreQuery,
    *,
    metric_registry: dict[str, ExploreMetricDefinition],
    breakdown_registry: dict[str, ExploreBreakdownDefinition] | None = None,
) -> ExploreValidationResult:
    """Validate an Explore query against registry constraints."""

    errors: list[str] = []
    warnings: list[str] = []

    if not query.schema_version:
        errors.append("Schema version is required.")
    elif query.schema_version != SCHEMA_VERSION:
        warnings.append(
            f"Schema version {query.schema_version} is not supported; results may be unavailable."
        )
        errors.append("Unsupported Explore query schema version.")

    if not query.player_id:
        errors.append("Player scope is required.")

    if not query.name.strip():
        errors.append("Query name is required.")

    if query.visualization_hint not in ("table", "bar", "donut", "kpi"):
        errors.append("Visualization hint is invalid.")

    if not query.metrics:
        errors.append("Metric selection is required.")

    metrics_by_key: dict[str, ExploreMetricDefinition] = {}
    for selection in query.metrics:
        metric = metric_registry.get(selection.key)
        if metric is None:
            errors.append(f"Unknown metric: {selection.key}.")
            continue
        metrics_by_key[selection.key] = metric
        if metric.deprecated_in_version:
            warnings.append(
                f"Metric {metric.label} is deprecated in {metric.deprecated_in_version} and may not render."
            )
        if selection.aggregation not in metric.allowed_aggregations:
            errors.append(
                f"Aggregation {selection.aggregation} is not allowed for metric {metric.label}."
            )
        if selection.percent_of_total and selection.aggregation not in ("sum", "count"):
            errors.append("Percent-of-total requires sum or count aggregation.")

    if not query.breakdowns and query.visualization_hint != "kpi":
        errors.append("At least one breakdown is required for this visualization.")
    if any(selection.percent_of_total for selection in query.metrics) and not query.breakdowns:
        errors.append("Percent-of-total requires at least one breakdown.")
    if any(selection.percent_of_total for selection in query.metrics) and query.visualization_hint == "kpi":
        errors.append("Percent-of-total is not supported for KPI output.")

    breakdown_registry = breakdown_registry or DEFAULT_BREAKDOWNS
    metric_group_breakdowns = 0
    for breakdown in query.breakdowns:
        definition = breakdown_registry.get(breakdown.dimension)
        if definition is None:
            errors.append(f"Unknown breakdown dimension: {breakdown.dimension}.")
            continue
        if definition.kind == "metric_group":
            metric_group_breakdowns += 1
            units = metric_units_for_breakdown(definition, metric_registry)
            if len(units) > 1:
                errors.append(
                    f"Breakdown {definition.label} mixes incompatible units: {', '.join(sorted(units))}."
                )
            for metric in metrics_by_key.values():
                if metric.unit not in units:
                    errors.append(
                        f"Metric {metric.label} is incompatible with breakdown {definition.label}."
                    )
                if (
                    definition.compatible_metric_keys
                    and metric.key not in definition.compatible_metric_keys
                ):
                    errors.append(
                        f"Metric {metric.label} is not supported for breakdown {definition.label}."
                    )

    if metric_group_breakdowns > 1:
        errors.append("Only one metric-group breakdown is supported at a time.")

    if query.visualization_hint == "donut" and len(query.breakdowns) > 1:
        errors.append("Donut charts support a single breakdown.")

    if query.visualization_hint in {"bar", "donut", "kpi"} and len(query.metrics) > 1:
        errors.append("Multiple metrics require table output.")

    if query.visualization_hint == "kpi" and query.breakdowns:
        warnings.append("KPI output ignores breakdowns and uses the total across the scope.")

    return ExploreValidationResult(errors=tuple(errors), warnings=tuple(warnings))


def parse_scope(scope: ExploreScope) -> dict[str, object | None]:
    """Return a serialized scope dict for storage."""

    return {
        "date_range": {
            "start": scope.start_date.isoformat() if scope.start_date else None,
            "end": scope.end_date.isoformat() if scope.end_date else None,
        },
        "tier": scope.tier,
        "preset": scope.preset_id,
        "snapshot": scope.snapshot_id,
        "past_n_runs": scope.past_n_runs,
        "include_hidden": scope.include_hidden,
    }


def parse_filters(filters: Iterable[ExploreFilter]) -> list[dict[str, object | None]]:
    """Return serialized filters for storage."""

    return [
        {
            "field": entry.field,
            "operator": entry.operator,
            "value": entry.value,
        }
        for entry in filters
    ]


def parse_breakdowns(breakdowns: Iterable[ExploreBreakdown]) -> list[dict[str, object]]:
    """Return serialized breakdowns for storage."""

    return [
        {
            "dimension": entry.dimension,
            "order": entry.order,
        }
        for entry in breakdowns
    ]


def parse_metric(metric: ExploreMetricSelection) -> dict[str, object]:
    """Return serialized metric selection."""

    return {
        "key": metric.key,
        "aggregation": metric.aggregation,
        "percent_of_total": metric.percent_of_total,
    }


def parse_metrics(metrics: Iterable[ExploreMetricSelection]) -> list[dict[str, object]]:
    """Return serialized metric selections."""

    return [parse_metric(metric) for metric in metrics]


def build_query_payload(query: ExploreQuery) -> dict[str, object]:
    """Serialize an ExploreQuery to a JSON-friendly payload."""

    return {
        "schema_version": query.schema_version,
        "player_id": query.player_id,
        "name": query.name,
        "scope": parse_scope(query.scope),
        "filters": parse_filters(query.filters),
        "breakdowns": parse_breakdowns(query.breakdowns),
        "metric": parse_metric(query.metrics[0]) if query.metrics else None,
        "metrics": parse_metrics(query.metrics),
        "visualization_hint": query.visualization_hint,
    }
