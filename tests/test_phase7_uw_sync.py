"""Phase 7 UW sync timeline tests."""

from __future__ import annotations

from analysis.uw_sync import UWTiming, compute_uw_sync_timeline


def test_uw_sync_timeline_computes_overlap_percent() -> None:
    """Compute a cumulative overlap percent without recommendations."""

    timeline = compute_uw_sync_timeline(
        [
            UWTiming(name="A", cooldown_seconds=10, duration_seconds=5),
            UWTiming(name="B", cooldown_seconds=10, duration_seconds=5),
            UWTiming(name="C", cooldown_seconds=10, duration_seconds=5),
        ],
        max_horizon_seconds=9,
        step_seconds=1,
    )
    assert timeline.horizon_seconds == 9
    assert timeline.overlap_percent_cumulative[-1] == 50.0

