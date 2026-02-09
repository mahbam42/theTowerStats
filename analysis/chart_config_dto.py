"""DTO schema for Phase 7 Chart Builder configurations.

The Chart Builder emits a constrained configuration that is:
- schema-driven (no free-form expressions),
- serializable for snapshots,
- validated before execution,
- consumed by the analysis layer to produce chart-ready DTO outputs.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Literal


ChartType = Literal["line", "bar", "area", "scatter", "donut"]
GroupBy = Literal["time", "tier", "preset"]
ComparisonMode = Literal["none", "before_after", "run_vs_run"]
SmoothingMode = Literal["none", "rolling_avg"]
XAxisMode = Literal["time", "metric"]
AggregationMode = Literal["sum", "avg"]


@dataclass(frozen=True, slots=True)
class ChartContextDTO:
    """Context filters attached to a chart configuration.

    Args:
        start_date: Optional inclusive lower bound date.
        end_date: Optional inclusive upper bound date.
        tier: Optional tier filter.
        tournament_filter: Optional tournament filter ("all" or specific rank key).
        preset_id: Optional preset id filter.
        excluded_preset_ids: Preset ids to exclude from the scope.
        include_tournaments: Whether tournament runs are included in the scope.
        patch_boundaries: Patch boundary dates used to define included windows.
    """

    start_date: date | None
    end_date: date | None
    tier: int | None = None
    tournament_filter: str | None = None
    preset_id: int | None = None
    excluded_preset_ids: tuple[int, ...] = ()
    include_tournaments: bool = False
    patch_boundaries: tuple[date, ...] = ()


@dataclass(frozen=True, slots=True)
class ChartScopeDTO:
    """A scope used by two-scope chart comparisons.

    Args:
        label: Display label for the scope.
        run_id: Optional BattleReport id used for run-vs-run comparisons.
        start_date: Optional inclusive start date used for before/after comparisons.
        end_date: Optional inclusive end date used for before/after comparisons.
    """

    label: str
    run_id: int | None = None
    start_date: date | None = None
    end_date: date | None = None


@dataclass(frozen=True, slots=True)
class ChartConfigDTO:
    """Constrained chart configuration produced by the Chart Builder.

    Args:
        metrics: One or more MetricSeries keys.
        chart_type: Visualization type.
        group_by: Grouping selection for splitting datasets.
        comparison: Optional two-scope comparison mode.
        smoothing: Optional smoothing mode (rolling average).
        aggregation: Optional aggregation override ("sum" or "avg").
        context: Context filters used when producing the chart.
        scopes: Exactly two scopes when `comparison != "none"`.
        x_axis: X-axis mode ("time" or metric-vs-metric).
        version: DTO version for forwards-compatible snapshot decoding.
    """

    metrics: tuple[str, ...]
    chart_type: ChartType
    group_by: GroupBy
    comparison: ComparisonMode
    smoothing: SmoothingMode
    context: ChartContextDTO
    aggregation: AggregationMode | None = None
    scopes: tuple[ChartScopeDTO, ChartScopeDTO] | None = None
    x_axis: XAxisMode = "time"
    version: str = "phase7_chart_config_v1"
