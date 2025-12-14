"""Delta calculations for the Analysis Engine.

This module computes deterministic differences between two values. Deltas are
computed on-demand and are never persisted.
"""

from __future__ import annotations

from .dto import MetricDelta


def delta(baseline: float, comparison: float) -> MetricDelta:
    """Compute absolute and percentage delta between two values.

    Args:
        baseline: Baseline value (A).
        comparison: Comparison value (B).

    Returns:
        MetricDelta with absolute and percentage changes. Percentage delta is
        None when the baseline is 0.
    """

    absolute = comparison - baseline
    percent: float | None
    if baseline == 0:
        percent = None
    else:
        percent = absolute / baseline
    return MetricDelta(
        baseline=baseline,
        comparison=comparison,
        absolute=absolute,
        percent=percent,
    )

