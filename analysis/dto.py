"""DTO types returned by the Analysis Engine.

DTOs are plain data containers used to transport analysis results to the UI.
They intentionally avoid any Django/ORM dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from datetime import date
from datetime import datetime

from .categories import MetricCategory


@dataclass(frozen=True)
class AnalysisResult:
    """Container for analysis results.

    Attributes:
        runs: Per-run analysis results.
    """

    runs: tuple["RunAnalysis", ...] = ()


@dataclass(frozen=True)
class RunProgressInput:
    """Minimal run-progress input used by Phase 1 analysis.

    Attributes:
        battle_date: The battle date to use as a time-series x-axis.
        coins: Total coins earned for the run.
        wave: Final wave reached.
        real_time_seconds: Run duration (seconds).
    """

    battle_date: datetime
    wave: int
    real_time_seconds: int
    coins: int | None = None


@dataclass(frozen=True)
class RunAnalysis:
    """Per-run analysis result.

    Attributes:
        run_id: Optional identifier for the underlying persisted record.
        battle_date: The battle date used as a time-series x-axis.
        tier: Optional tier value when available on the input.
        preset_name: Optional preset label when available on the input.
        coins_per_hour: Derived rate metric for Phase 1 charts.
    """

    run_id: int | None
    battle_date: datetime
    tier: int | None
    preset_name: str | None
    coins_per_hour: float


@dataclass(frozen=True, slots=True)
class MetricDefinition:
    """Definition for an observed or derived metric.

    Attributes:
        key: Stable metric key used by UI selection and charting.
        label: Human-friendly label.
        unit: Display unit string (e.g. "coins/hour", "seconds").
        category: Semantic category used for filtering and validation.
        kind: Either "observed" or "derived".
    """

    key: str
    label: str
    unit: str
    category: MetricCategory
    kind: str


@dataclass(frozen=True, slots=True)
class UsedParameter:
    """A parameter value referenced during derived metric computation.

    Attributes:
        entity_type: High-level entity type (card, ultimate_weapon, guardian_chip, bot).
        entity_name: Human-friendly entity name.
        key: Parameter key used by the computation.
        raw_value: Raw string as stored.
        normalized_value: Best-effort normalized float value, if parseable.
        wiki_revision_id: Optional wiki revision id (core.WikiData pk) used.
    """

    entity_type: str
    entity_name: str
    key: str
    raw_value: str
    normalized_value: float | None
    wiki_revision_id: int | None


@dataclass(frozen=True)
class MetricPoint:
    """A per-run metric point for charting.

    Attributes:
        run_id: Optional identifier for the underlying persisted record.
        battle_date: Timestamp used as the x-axis.
        tier: Optional tier value when available.
        preset_name: Optional preset label when available.
        value: Metric value, or None when inputs are missing.
    """

    run_id: int | None
    battle_date: datetime
    tier: int | None
    preset_name: str | None
    value: float | None


@dataclass(frozen=True)
class MetricSeriesResult:
    """A computed time series for a selected metric.

    Attributes:
        metric: MetricDefinition describing the series.
        points: Per-run metric points.
        used_parameters: Parameters referenced (for derived metrics and UI transparency).
        assumptions: Human-readable, non-prescriptive notes about formulas/policies.
    """

    metric: MetricDefinition
    points: tuple[MetricPoint, ...] = ()
    used_parameters: tuple[UsedParameter, ...] = ()
    assumptions: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class MetricDelta:
    """A deterministic delta between two numeric metric values.

    Attributes:
        baseline: Baseline value (A).
        comparison: Comparison value (B).
        absolute: `comparison - baseline`.
        percent: `(comparison - baseline) / baseline`, or None when baseline is 0.
    """

    baseline: float
    comparison: float
    absolute: float
    percent: float | None


@dataclass(frozen=True)
class WindowSummary:
    """A summarized view of runs within a date window.

    Attributes:
        start_date: Window start date (inclusive).
        end_date: Window end date (inclusive).
        run_count: Number of runs included in the window.
        average_coins_per_hour: Average coins/hour across runs, if any.
    """

    start_date: date
    end_date: date
    run_count: int
    average_coins_per_hour: float | None
