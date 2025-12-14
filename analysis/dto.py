"""DTO types returned by the Analysis Engine.

DTOs are plain data containers used to transport analysis results to the UI.
They intentionally avoid any Django/ORM dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from datetime import datetime


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
