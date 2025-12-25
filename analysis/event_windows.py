"""Event-window helpers for charts and dashboards.

The Tower in-game Events run in fixed 14-day windows. This module provides pure
helpers (no Django imports) to compute and shift those windows deterministically.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta


EVENT_WINDOW_DAYS = 14


@dataclass(frozen=True, slots=True)
class EventWindow:
    """A 14-day inclusive date window used by in-game Events.

    Attributes:
        start: Inclusive window start date.
        end: Inclusive window end date.
    """

    start: date
    end: date


def event_window_for_date(*, target: date, anchor: date, window_days: int = EVENT_WINDOW_DAYS) -> EventWindow:
    """Return the Event window containing a target date.

    Args:
        target: The date to place into an Event window.
        anchor: A known Event start date (inclusive) used as the stepping origin.
        window_days: Window size in days (defaults to 14).

    Returns:
        EventWindow containing `target`, with an inclusive `end` date.
    """

    if window_days <= 0:
        raise ValueError("window_days must be positive.")

    offset_days = (target - anchor).days
    window_index = offset_days // window_days
    start = anchor + timedelta(days=window_index * window_days)
    end = start + timedelta(days=window_days - 1)
    return EventWindow(start=start, end=end)


def shift_event_window(window: EventWindow, *, shift: int, window_days: int = EVENT_WINDOW_DAYS) -> EventWindow:
    """Shift an Event window forward/backward by N windows.

    Args:
        window: The base EventWindow to shift.
        shift: Number of windows to shift; negative means previous.
        window_days: Window size in days (defaults to 14).

    Returns:
        Shifted EventWindow.
    """

    if window_days <= 0:
        raise ValueError("window_days must be positive.")
    delta = timedelta(days=shift * window_days)
    return EventWindow(start=window.start + delta, end=window.end + delta)


def coerce_window_bounds(*, start: date | None, end: date | None, window_days: int = EVENT_WINDOW_DAYS) -> EventWindow:
    """Coerce partial start/end inputs into a full inclusive window.

    This helper is used by event navigation controls so that shifting always
    has both a start and an end.

    Args:
        start: Optional inclusive start date.
        end: Optional inclusive end date.
        window_days: Window size in days (defaults to 14).

    Returns:
        EventWindow whose bounds match provided inputs when possible.
    """

    if window_days <= 0:
        raise ValueError("window_days must be positive.")

    if start is None and end is None:
        raise ValueError("At least one of start/end must be provided.")

    if start is None and end is not None:
        start = end - timedelta(days=window_days - 1)
    if end is None and start is not None:
        end = start + timedelta(days=window_days - 1)
    assert start is not None and end is not None
    return EventWindow(start=start, end=end)

