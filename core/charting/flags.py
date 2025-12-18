"""Deterministic run flags for charts.

Flags are advisory signals that help a user interpret charts. They never change
metric values and must avoid probabilistic language.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from statistics import median
from typing import Iterable


@dataclass(frozen=True, slots=True)
class FlagRule:
    """A single chart flag rule.

    Args:
        key: Stable key used for programmatic matching.
        label: Short label for UI display.
        description: Plain-language explanation of what triggered the flag.
    """

    key: str
    label: str
    description: str


INCOMPLETE_RUN: FlagRule = FlagRule(
    key="incomplete_run",
    label="Incomplete run",
    description="Incomplete run metadata (wave/time missing).",
)

ROLLING_MEDIAN_DEVIATION: FlagRule = FlagRule(
    key="rolling_median_deviation",
    label="Deviation",
    description="Value differs from the rolling median by more than 3×.",
)

PATCH_BOUNDARY: FlagRule = FlagRule(
    key="patch_boundary",
    label="Boundary",
    description="Marked boundary date (data may not be comparable across the boundary).",
)


def rolling_median_flags(values: list[float | None], *, window: int = 7) -> list[bool]:
    """Return a boolean list indicating rolling-median deviations.

    Args:
        values: Numeric series aligned to chart labels, with None for missing points.
        window: Lookback window size used for computing the reference median.

    Returns:
        A list of booleans aligned to `values`, True where a point is flagged.
    """

    out: list[bool] = [False for _ in values]
    for idx, value in enumerate(values):
        if value is None:
            continue
        start = max(0, idx - max(window, 1))
        history = [v for v in values[start:idx] if v is not None]
        if len(history) < 3:
            continue
        reference = median(history)
        if reference <= 0:
            continue
        ratio = value / reference if reference else 0.0
        if ratio >= 3.0 or ratio <= (1.0 / 3.0):
            out[idx] = True
    return out


def apply_patch_boundaries(
    labels: list[str],
    *,
    boundary_dates: Iterable[date],
) -> list[bool]:
    """Return a boolean list indicating label dates matching known boundaries.

    Args:
        labels: ISO date labels ("YYYY-MM-DD").
        boundary_dates: Boundary dates considered important for interpretation.

    Returns:
        A list aligned to `labels`, True for boundary dates.
    """

    boundaries = {d.isoformat() for d in boundary_dates}
    return [label in boundaries for label in labels]

