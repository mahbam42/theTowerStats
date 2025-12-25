"""Chart Builder helpers for generating runtime ChartConfig instances.

The Charts dashboard already supports declarative ChartConfig entries. Phase 7
adds a constrained Chart Builder that constructs ChartConfig values from a
limited set of user selections, then validates them using the same validator
used for built-in charts.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Literal

from analysis.categories import MetricCategory
from analysis.series_registry import DEFAULT_REGISTRY

from .schema import (
    ChartCategory,
    ChartComparison,
    ChartConfig,
    ChartDomain,
    ChartFilters,
    ChartSeriesConfig,
    ChartUI,
    ComparisonScope,
    DateRangeFilterConfig,
    SimpleFilterConfig,
)


ChartBuilderChartType = Literal["line", "bar", "donut"]
ChartBuilderGroupBy = Literal["time", "tier", "preset"]
ChartBuilderComparison = Literal["none", "before_after", "run_vs_run"]
ChartBuilderSmoothing = Literal["none", "rolling_avg"]


@dataclass(frozen=True, slots=True)
class ChartBuilderSelection:
    """Validated, typed selections used to build a runtime chart.

    Args:
        metric_keys: One or more MetricSeries keys selected by the user.
        chart_type: The chart type requested by the user.
        group_by: Grouping control for splitting the chart (tier/preset).
        comparison: Optional two-scope comparison mode.
        smoothing: Optional smoothing control (rolling average).
        scope_a: Scope A when `comparison` is enabled.
        scope_b: Scope B when `comparison` is enabled.
    """

    metric_keys: tuple[str, ...]
    chart_type: ChartBuilderChartType
    group_by: ChartBuilderGroupBy
    comparison: ChartBuilderComparison
    smoothing: ChartBuilderSmoothing
    scope_a: ComparisonScope | None = None
    scope_b: ComparisonScope | None = None


def build_runtime_chart_config(selection: ChartBuilderSelection) -> ChartConfig:
    """Build a runtime ChartConfig from a Chart Builder selection.

    Args:
        selection: Validated chart builder selections.

    Returns:
        ChartConfig compatible with the existing dashboard renderer.
    """

    default_start = datetime(2025, 12, 9, 0, 0, 0, tzinfo=UTC)
    metric_series = tuple(
        ChartSeriesConfig(
            metric_key=key,
            transform="moving_average" if selection.smoothing == "rolling_avg" else "none",
        )
        for key in selection.metric_keys
    )

    filters = ChartFilters(
        date_range=DateRangeFilterConfig(enabled=True, default_start=default_start),
        tier=SimpleFilterConfig(enabled=True),
        preset=SimpleFilterConfig(enabled=True),
    )

    comparison: ChartComparison | None = None
    inferred_domain = _infer_domain(selection.metric_keys)
    category: ChartCategory = inferred_domain
    if selection.comparison != "none":
        category = "comparison"
        if selection.scope_a is not None and selection.scope_b is not None:
            comparison = ChartComparison(
                mode="run_vs_run" if selection.comparison == "run_vs_run" else "before_after",
                scopes=(selection.scope_a, selection.scope_b),
            )
    elif selection.group_by == "tier":
        category = "comparison"
        comparison = ChartComparison(mode="by_tier")
    elif selection.group_by == "preset":
        category = "comparison"
        comparison = ChartComparison(mode="by_preset")

    return ChartConfig(
        id="chart_builder_custom",
        title="Custom chart",
        description="Chart Builder output (not persisted).",
        category=category,
        domain=inferred_domain,
        semantic_type="distribution" if selection.chart_type == "donut" else "absolute",
        chart_type=selection.chart_type,  # type: ignore[arg-type]
        metric_series=metric_series,
        filters=filters,
        comparison=comparison,
        derived=None,
        ui=ChartUI(show_by_default=False, selectable=False, order=0),
    )


def _infer_domain(metric_keys: tuple[str, ...]) -> ChartDomain:
    """Infer a chart domain for Chart Builder selections.

    Args:
        metric_keys: MetricSeries keys selected in the builder.

    Returns:
        Best-effort ChartDomain based on the registered metric categories.
    """

    domains: set[ChartDomain] = set()
    for key in metric_keys:
        spec = DEFAULT_REGISTRY.get(key)
        if spec is None:
            continue
        domains.add(_domain_for_category(spec.category))
    if len(domains) == 1:
        return next(iter(domains))
    return "economy"


def _domain_for_category(category: MetricCategory) -> ChartDomain:
    """Map a MetricCategory to a ChartDomain."""

    if category in (MetricCategory.damage, MetricCategory.combat):
        return "damage"
    if category == MetricCategory.enemy_destruction:
        return "enemy_destruction"
    if category == MetricCategory.efficiency:
        return "efficiency"
    if category == MetricCategory.utility:
        return "efficiency"
    return "economy"

def build_before_after_scopes(
    *,
    window_a_start: date,
    window_a_end: date,
    window_b_start: date,
    window_b_end: date,
    label_a: str = "Window A",
    label_b: str = "Window B",
) -> tuple[ComparisonScope, ComparisonScope]:
    """Build ComparisonScope values for a before/after chart comparison.

    Args:
        window_a_start: Inclusive start for scope A.
        window_a_end: Inclusive end for scope A.
        window_b_start: Inclusive start for scope B.
        window_b_end: Inclusive end for scope B.
        label_a: Display label for scope A.
        label_b: Display label for scope B.

    Returns:
        Two ComparisonScope objects (A, B).
    """

    return (
        ComparisonScope(label=label_a, start_date=window_a_start, end_date=window_a_end),
        ComparisonScope(label=label_b, start_date=window_b_start, end_date=window_b_end),
    )


def build_run_vs_run_scopes(
    *,
    run_a_id: int,
    run_b_id: int,
    label_a: str = "Run A",
    label_b: str = "Run B",
) -> tuple[ComparisonScope, ComparisonScope]:
    """Build ComparisonScope values for a run-vs-run chart comparison.

    Args:
        run_a_id: BattleReport id for scope A.
        run_b_id: BattleReport id for scope B.
        label_a: Display label for scope A.
        label_b: Display label for scope B.

    Returns:
        Two ComparisonScope objects (A, B).
    """

    return (
        ComparisonScope(label=label_a, run_id=run_a_id),
        ComparisonScope(label=label_b, run_id=run_b_id),
    )
