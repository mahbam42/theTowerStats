"""Derived tournament classification for Battle Report runs.

Tournament runs in The Tower can be inferred from the Battle Report tier label
format (e.g. `3+`, `5+`, `8+`). This module centralizes the logic so templates
and JavaScript do not need to re-implement ad-hoc checks.
"""

from __future__ import annotations

import re

_TIER_LINE_RE = re.compile(r"(?im)^[ \t]*Tier[ \t]*[:\t][ \t]*(?P<value>.*?)[ \t]*$")
_TOURNAMENT_TIER_RE = re.compile(r"^[ \t]*(?P<bracket>\d+)[ \t]*\+[ \t]*$")


def extract_tier_label(raw_text: str) -> str | None:
    """Extract the raw Tier label from Battle Report text.

    Args:
        raw_text: Raw Battle Report text.

    Returns:
        The tier label as written (trimmed), or None if not present.
    """

    match = _TIER_LINE_RE.search(raw_text)
    if match is None:
        return None
    value = (match.group("value") or "").strip()
    return value or None


def tournament_bracket(run: object) -> str | None:
    """Return the tournament bracket label for a run, if present.

    Args:
        run: A BattleReport-like object (has `raw_text`), a Progress-like object
            (has `battle_report.raw_text`), or any object with either shape.

    Returns:
        A normalized bracket label like `3+`, or None if the run is not a
        tournament run.
    """

    raw_text = _raw_text_from_run(run)
    if not raw_text:
        return None

    tier_label = extract_tier_label(raw_text)
    if tier_label is None:
        return None

    match = _TOURNAMENT_TIER_RE.match(tier_label)
    if match is None:
        return None
    return f"{match.group('bracket')}+"


def is_tournament(run: object) -> bool:
    """Return True when a run is inferred to be a tournament run.

    Args:
        run: A BattleReport-like object (has `raw_text`), a Progress-like object
            (has `battle_report.raw_text`), or any object with either shape.

    Returns:
        True if the Tier label matches the tournament format (e.g. `3+`).
    """

    return tournament_bracket(run) is not None


def _raw_text_from_run(run: object) -> str | None:
    """Best-effort extraction of raw report text from common run objects."""

    if isinstance(run, str):
        return run

    raw_text = getattr(run, "raw_text", None)
    if isinstance(raw_text, str) and raw_text:
        return raw_text

    battle_report = getattr(run, "battle_report", None)
    if battle_report is not None:
        nested = getattr(battle_report, "raw_text", None)
        if isinstance(nested, str) and nested:
            return nested

    run_progress = getattr(run, "run_progress", None)
    if run_progress is not None:
        return _raw_text_from_run(run_progress)

    return None
