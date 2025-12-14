"""DTO types returned by the Analysis Engine.

DTOs are plain data containers used to transport analysis results to the UI.
They intentionally avoid any Django/ORM dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AnalysisResult:
    """Container for analysis results.

    This is a placeholder DTO used during initial scaffolding.
    """


@dataclass(frozen=True)
class RunAnalysis:
    """Per-run analysis result.

    This is a placeholder DTO used during initial scaffolding.
    """

