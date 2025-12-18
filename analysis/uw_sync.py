"""Deterministic Ultimate Weapon sync timeline helpers.

This module provides descriptive calculations for cooldown/duration alignment.
It does not recommend timing changes and does not require database access.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import gcd
from typing import Iterable


@dataclass(frozen=True, slots=True)
class UWTiming:
    """Timing inputs for a single Ultimate Weapon.

    Args:
        name: Display name.
        cooldown_seconds: Cooldown in seconds (must be > 0).
        duration_seconds: Active duration in seconds (must be >= 0).
    """

    name: str
    cooldown_seconds: int
    duration_seconds: int


@dataclass(frozen=True, slots=True)
class UWSyncTimeline:
    """Computed sync timeline suitable for charting.

    Args:
        labels: Timeline labels ("t=0s", ...).
        active_by_uw: Mapping of UW name to 0/1 activity list aligned to labels.
        overlap_all: 0/1 list aligned to labels where all entries are active.
        overlap_percent_cumulative: Cumulative overlap percent (0–100) aligned to labels.
        horizon_seconds: Total modeled horizon in seconds.
    """

    labels: list[str]
    active_by_uw: dict[str, list[int]]
    overlap_all: list[int]
    overlap_percent_cumulative: list[float]
    horizon_seconds: int


def _lcm(a: int, b: int) -> int:
    """Return least common multiple for positive integers."""

    return abs(a * b) // gcd(a, b) if a and b else 0


def compute_uw_sync_timeline(
    timings: Iterable[UWTiming],
    *,
    max_horizon_seconds: int = 1800,
    step_seconds: int = 1,
) -> UWSyncTimeline:
    """Compute a descriptive sync timeline for a set of UWs.

    Args:
        timings: Iterable of UWTiming entries (typically 3).
        max_horizon_seconds: Upper bound for the modeled horizon.
        step_seconds: Step size in seconds for timeline sampling.

    Returns:
        UWSyncTimeline suitable for rendering with a line/step chart.

    Raises:
        ValueError: When timings are invalid (non-positive cooldowns, negative durations).
    """

    entries = list(timings)
    if not entries:
        raise ValueError("At least one UWTiming entry is required.")

    for entry in entries:
        if entry.cooldown_seconds <= 0:
            raise ValueError(f"{entry.name} cooldown must be > 0 seconds.")
        if entry.duration_seconds < 0:
            raise ValueError(f"{entry.name} duration must be >= 0 seconds.")

    horizon = entries[0].cooldown_seconds
    for entry in entries[1:]:
        horizon = _lcm(horizon, entry.cooldown_seconds)
    if horizon <= 0:
        horizon = max(entry.cooldown_seconds for entry in entries)
    horizon = min(horizon, max_horizon_seconds)
    step = max(1, int(step_seconds))

    labels: list[str] = []
    active_by_uw: dict[str, list[int]] = {entry.name: [] for entry in entries}
    overlap_all_three: list[int] = []
    overlap_percent_cumulative: list[float] = []

    overlap_so_far = 0
    count = 0
    for t in range(0, horizon + 1, step):
        labels.append(f"{t}s")
        states = []
        for entry in entries:
            active = 1 if (t % entry.cooldown_seconds) < entry.duration_seconds else 0
            active_by_uw[entry.name].append(active)
            states.append(active)

        overlap = 1 if all(states) else 0
        overlap_all_three.append(overlap)
        overlap_so_far += overlap
        count += 1
        overlap_percent_cumulative.append(round((overlap_so_far / count) * 100.0, 2))

    return UWSyncTimeline(
        labels=labels,
        active_by_uw=active_by_uw,
        overlap_all=overlap_all_three,
        overlap_percent_cumulative=overlap_percent_cumulative,
        horizon_seconds=horizon,
    )
