"""DTO schema for Phase 7 Chart Builder inputs.

This schema mirrors the constrained Chart Builder contract and is designed to
be serialized (e.g., into snapshots) without carrying UI or database concerns.
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
    """Context filters attached to a Chart Builder configuration.

    Args:
        start_date: Optional inclusive lower bound date.
        end_date: Optional inclusive upper bound date.
        tier: Optional tier filter value.
        preset_id: Optional preset identifier.
    """

    start_date: date | None
    end_date: date | None
    tier: int | None = None
    preset_id: int | None = None


@dataclass(frozen=True, slots=True)
class ChartConfigDTO:
    """Constrained chart configuration produced by the Chart Builder.

    Args:
        metrics: One or more MetricSeries keys.
        chart_type: Visualization type (line/bar/donut).
        group_by: Grouping axis (time/tier/preset).
        comparison: Two-scope comparison mode.
        smoothing: Optional smoothing mode.
        context: Context filters applied when building the chart.
    """

    metrics: tuple[str, ...]
    chart_type: ChartType
    group_by: GroupBy
    comparison: ComparisonMode
    smoothing: SmoothingMode
    context: ChartContextDTO

