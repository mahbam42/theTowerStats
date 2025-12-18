"""Schema types for declarative chart configuration.

The Charts dashboard is driven by configuration objects (ChartConfig) instead
of hard-coded chart logic. This keeps the rendering layer generic and makes it
possible to add charts without touching view code.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from datetime import datetime
from typing import Literal

ChartCategory = Literal[
    "top_level",
    "sub_chart",
    "uw_performance",
    "guardian_stats",
    "bot_stats",
    "comparison",
    "derived",
]

ChartType = Literal["line", "bar", "area", "scatter", "donut"]

MetricTransform = Literal["none", "moving_average", "cumulative", "rate_per_hour"]

ComparisonMode = Literal[
    "none",
    "by_tier",
    "by_preset",
    "by_entity",
    "before_after",
    "run_vs_run",
]

XAxis = Literal["time", "wave_number"]


@dataclass(frozen=True, slots=True)
class DateRangeFilterConfig:
    """Configure an optional date-range filter for a chart.

    Args:
        enabled: Whether the chart accepts date range filtering.
        default_start: Default lower bound for the date range.
    """

    enabled: bool
    default_start: datetime


@dataclass(frozen=True, slots=True)
class SimpleFilterConfig:
    """Configure a simple boolean-enabled filter."""

    enabled: bool


@dataclass(frozen=True, slots=True)
class ChartFilters:
    """Filter toggles for a chart configuration."""

    date_range: DateRangeFilterConfig
    tier: SimpleFilterConfig = SimpleFilterConfig(enabled=False)
    preset: SimpleFilterConfig = SimpleFilterConfig(enabled=False)
    uw: SimpleFilterConfig = SimpleFilterConfig(enabled=False)
    guardian: SimpleFilterConfig = SimpleFilterConfig(enabled=False)
    bot: SimpleFilterConfig = SimpleFilterConfig(enabled=False)


@dataclass(frozen=True, slots=True)
class ChartSeriesConfig:
    """A single metric series used by a chart.

    Args:
        metric_key: Registered MetricSeries key.
        label: Optional override label for the series.
        transform: Optional transform applied to the series values.
    """

    metric_key: str
    label: str | None = None
    transform: MetricTransform = "none"


@dataclass(frozen=True, slots=True)
class ChartComparison:
    """Optional comparison behavior for a chart configuration.

    The comparison layer supports two styles:

    - Grouping comparisons (by tier/preset) that split a single scope into
      multiple datasets.
    - Two-scope comparisons (before/after, run vs run) that split the same
      config into exactly two datasets.
    """

    mode: ComparisonMode
    entities: tuple[str, ...] | None = None
    scopes: tuple["ComparisonScope", "ComparisonScope"] | None = None


@dataclass(frozen=True, slots=True)
class ComparisonScope:
    """A concrete scope used by two-scope chart comparisons.

    Args:
        label: Display label for the scope (shown in chart legends).
        run_id: Optional BattleReport id for run-vs-run comparisons.
        start_date: Optional inclusive window start (used by before/after).
        end_date: Optional inclusive window end (used by before/after).
    """

    label: str
    run_id: int | None = None
    start_date: date | None = None
    end_date: date | None = None


@dataclass(frozen=True, slots=True)
class ChartDerived:
    """Derived metric configuration computed from other series keys."""

    formula: str
    x_axis: XAxis = "time"


@dataclass(frozen=True, slots=True)
class ChartUI:
    """UI presentation hints for charts."""

    show_by_default: bool
    selectable: bool
    order: int


@dataclass(frozen=True, slots=True)
class ChartConfig:
    """Declarative chart definition for the dashboard.

    Args:
        id: Stable, unique identifier used by the dashboard selection control.
        title: Chart title displayed in the UI.
        description: Optional chart description shown in selection lists/tooltips.
        category: Used for grouping charts in the selection UI.
        chart_type: The visual chart type.
        metric_series: One or more metric series definitions that feed the chart.
        filters: Filter toggles, including default date range behavior.
        comparison: Optional comparison behavior (generates multiple datasets).
        derived: Optional derived metric definition (computed from series inputs).
        ui: UI behavior flags (default selection, ordering, etc).
    """

    id: str
    title: str
    description: str | None
    category: ChartCategory
    chart_type: ChartType
    metric_series: tuple[ChartSeriesConfig, ...]
    filters: ChartFilters
    comparison: ChartComparison | None = None
    derived: ChartDerived | None = None
    ui: ChartUI = ChartUI(show_by_default=False, selectable=True, order=999)
