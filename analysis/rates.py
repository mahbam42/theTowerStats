"""Rate calculations for the Analysis Engine.

Phase 1 intentionally ships a single derived rate metric: waves per hour.
"""

from __future__ import annotations


def waves_per_hour(wave: int, real_time_seconds: int) -> float | None:
    """Compute waves per hour for a single run.

    Args:
        wave: Final wave reached.
        real_time_seconds: Run duration in seconds.

    Returns:
        Waves per hour, or None when inputs are invalid.
    """

    if wave <= 0:
        return None
    if real_time_seconds <= 0:
        return None
    return (wave * 3600.0) / float(real_time_seconds)
