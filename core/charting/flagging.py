"""Flagging helpers used by chart rendering.

These helpers are UI-adjacent but remain deterministic and value-preserving.
"""

from __future__ import annotations

from datetime import date
from typing import Iterable

from core.charting.flags import (
    INCOMPLETE_RUN,
    PATCH_BOUNDARY,
    ROLLING_MEDIAN_DEVIATION,
    apply_patch_boundaries,
    rolling_median_flags,
)


def incomplete_run_labels(records: Iterable[object]) -> set[str]:
    """Return ISO date labels that contain at least one incomplete run.

    Args:
        records: Typically a BattleReport QuerySet filtered to the current context.

    Returns:
        Set of ISO date strings ("YYYY-MM-DD") where a run is missing key metadata.
    """

    labels: set[str] = set()
    for record in records:
        progress = getattr(record, "run_progress", None)
        battle_date = getattr(progress, "battle_date", None)
        if battle_date is None:
            continue
        wave = getattr(progress, "wave", None)
        real_time = getattr(progress, "real_time_seconds", None)
        if wave is None or real_time is None:
            labels.add(battle_date.date().isoformat())
    return labels


def flag_reasons(
    labels: list[str],
    *,
    values: list[float | None],
    incomplete_labels: set[str],
    patch_boundaries: tuple[date, ...],
) -> list[str | None]:
    """Compute per-point flag reasons aligned to labels.

    Args:
        labels: ISO date labels for the series.
        values: Series values aligned to labels.
        incomplete_labels: Set of labels containing incomplete run metadata.
        patch_boundaries: Known boundary dates (optional).

    Returns:
        List of optional reason strings aligned to `labels`.
    """

    reasons: list[list[str]] = [[] for _ in labels]

    for idx, label in enumerate(labels):
        if label in incomplete_labels:
            reasons[idx].append(INCOMPLETE_RUN.description)

    for idx, flagged in enumerate(rolling_median_flags(values, window=7)):
        if flagged:
            reasons[idx].append(ROLLING_MEDIAN_DEVIATION.description)

    for idx, flagged in enumerate(apply_patch_boundaries(labels, boundary_dates=patch_boundaries)):
        if flagged:
            reasons[idx].append(PATCH_BOUNDARY.description)

    return ["; ".join(items) if items else None for items in reasons]

