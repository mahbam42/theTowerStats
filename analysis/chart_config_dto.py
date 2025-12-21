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


ChartType = Literal["line", "bar", "donut"]
GroupBy = Literal["time", "tier", "preset"]
ComparisonMode = Literal["none", "before_after", "run_vs_run"]
SmoothingMode = Literal["none", "rolling_avg"]


@dataclass(frozen=True, slots=True)
class ChartContextDTO:
    """Context filters attached to a chart configuration.

    Args:
        start_date: Optional inclusive lower bound date.
        end_date: Optional inclusive upper bound date.
        tier: Optional tier filter.
        preset_id: Optional preset id filter.
        include_tournaments: Whether tournament runs are included in the scope.
    """

    start_date: date | None
    end_date: date | None
    tier: int | None = None
    preset_id: int | None = None
    include_tournaments: bool = False


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
        context: Context filters used when producing the chart.
        scopes: Exactly two scopes when `comparison != "none"`.
        version: DTO version for forwards-compatible snapshot decoding.
    """

    metrics: tuple[str, ...]
    chart_type: ChartType
    group_by: GroupBy
    comparison: ComparisonMode
    smoothing: SmoothingMode
    context: ChartContextDTO
    scopes: tuple[ChartScopeDTO, ChartScopeDTO] | None = None
    version: str = "phase7_chart_config_v1"
