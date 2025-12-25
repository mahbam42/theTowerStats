"""Unit tests for in-game Event window helpers."""

from __future__ import annotations

from datetime import date

import pytest

from analysis.event_windows import EventWindow, coerce_window_bounds, event_window_for_date, shift_event_window

pytestmark = pytest.mark.unit


def test_event_window_for_date_includes_anchor_start() -> None:
    """Anchor date should map to the first inclusive 14-day window."""

    anchor = date(2025, 12, 9)
    window = event_window_for_date(target=anchor, anchor=anchor)
    assert window == EventWindow(start=date(2025, 12, 9), end=date(2025, 12, 22))


def test_event_window_for_date_rolls_forward_on_day_14() -> None:
    """Day 14 after the anchor should land in the next window."""

    anchor = date(2025, 12, 9)
    window = event_window_for_date(target=date(2025, 12, 23), anchor=anchor)
    assert window.start == date(2025, 12, 23)
    assert window.end == date(2026, 1, 5)


def test_event_window_for_date_rolls_backward_before_anchor() -> None:
    """Dates before the anchor should step backward in 14-day increments."""

    anchor = date(2025, 12, 9)
    window = event_window_for_date(target=date(2025, 12, 8), anchor=anchor)
    assert window.start == date(2025, 11, 25)
    assert window.end == date(2025, 12, 8)


def test_shift_event_window_moves_by_one_window() -> None:
    """Shift should move both bounds by 14 days."""

    window = EventWindow(start=date(2025, 12, 9), end=date(2025, 12, 22))
    shifted = shift_event_window(window, shift=1)
    assert shifted.start == date(2025, 12, 23)
    assert shifted.end == date(2026, 1, 5)


def test_coerce_window_bounds_requires_one_side() -> None:
    """Coercion should reject empty bounds."""

    with pytest.raises(ValueError, match="start/end"):
        coerce_window_bounds(start=None, end=None)


def test_coerce_window_bounds_fills_missing_end() -> None:
    """Coercion should fill missing end based on the window size."""

    window = coerce_window_bounds(start=date(2025, 12, 9), end=None)
    assert window.start == date(2025, 12, 9)
    assert window.end == date(2025, 12, 22)
