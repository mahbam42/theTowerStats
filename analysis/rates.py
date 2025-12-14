"""Rate calculations for the Analysis Engine.

Phase 1 intentionally ships a single derived rate metric: coins per hour.
"""

from __future__ import annotations


def coins_per_hour(coins: int, real_time_seconds: int) -> float | None:
    """Compute coins per hour for a single run.

    Args:
        coins: Total coins earned.
        real_time_seconds: Run duration in seconds.

    Returns:
        Coins per hour, or None when inputs are invalid.
    """

    if coins <= 0:
        return None
    if real_time_seconds <= 0:
        return None
    return (coins * 3600.0) / float(real_time_seconds)
