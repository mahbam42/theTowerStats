"""DTO types returned by the Analysis Engine.

DTOs are plain data containers used to transport analysis results to the UI.
They intentionally avoid any Django/ORM dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass
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
        battle_date: The battle date used as a time-series x-axis.
        coins_per_hour: Derived rate metric for Phase 1 charts.
    """

    battle_date: datetime
    coins_per_hour: float
