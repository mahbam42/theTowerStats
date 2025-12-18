"""Build descriptive UW sync payloads for UI rendering."""

from __future__ import annotations

import re
from dataclasses import dataclass

from analysis.uw_sync import UWTiming, compute_uw_sync_timeline
from definitions.models import ParameterKey
from player_state.models import Player, PlayerBot, PlayerUltimateWeapon


@dataclass(frozen=True, slots=True)
class UWSyncPayload:
    """Template-ready payload for the UW sync chart.

    Args:
        chart_data: Chart.js data payload (labels + datasets).
        summary: Short summary values for display next to the chart.
    """

    chart_data: dict[str, object]
    summary: dict[str, object]


def _extract_seconds(value_raw: str) -> int | None:
    """Extract an integer seconds value from a raw parameter string.

    Args:
        value_raw: Raw value string (e.g. "120s", "120", "120.0").

    Returns:
        Parsed seconds rounded to the nearest int, or None when not parseable.
    """

    match = re.search(r"([0-9]+(?:\\.[0-9]+)?)", (value_raw or "").replace(",", ""))
    if not match:
        return None
    try:
        return int(round(float(match.group(1))))
    except ValueError:
        return None


def build_uw_sync_payload(*, player: Player) -> UWSyncPayload | None:
    """Return a UW sync chart payload when required inputs are available.

    Args:
        player: Player used to look up Ultimate Weapon parameter state.

    Returns:
        UWSyncPayload when Golden Tower, Black Hole, and Death Wave are unlocked
        and have parseable cooldown/duration values; otherwise None.
    """

    required_uws = (
        ("golden_tower", "Golden Tower"),
        ("black_hole", "Black Hole"),
        ("death_wave", "Death Wave"),
    )

    uws: list[tuple[str, str, PlayerUltimateWeapon]] = []
    for slug, display in required_uws:
        uw = (
            PlayerUltimateWeapon.objects.filter(player=player, ultimate_weapon_slug=slug)
            .select_related("ultimate_weapon_definition")
            .prefetch_related("parameters__parameter_definition")
            .first()
        )
        if uw is None or not uw.unlocked:
            return None
        uws.append((slug, display, uw))

    timings: list[UWTiming] = []
    for slug, display, uw in uws:
        params = list(uw.parameters.all())
        cooldown_raw = next(
            (
                p.effective_value_raw
                for p in params
                if p.parameter_definition is not None and p.parameter_definition.key == ParameterKey.COOLDOWN.value
            ),
            "",
        )
        duration_raw = next(
            (
                p.effective_value_raw
                for p in params
                if p.parameter_definition is not None and p.parameter_definition.key == ParameterKey.DURATION.value
            ),
            "",
        )
        cooldown = _extract_seconds(cooldown_raw)
        duration = _extract_seconds(duration_raw)
        if cooldown is None or duration is None:
            return None
        timings.append(UWTiming(name=display, cooldown_seconds=cooldown, duration_seconds=duration))

    golden_bot_timing = _golden_bot_timing(player=player)
    if golden_bot_timing is not None:
        timings.append(golden_bot_timing)

    timeline = compute_uw_sync_timeline(timings, max_horizon_seconds=1800, step_seconds=1)

    datasets: list[dict[str, object]] = []
    palette = {
        "Golden Tower": "#DC3912",
        "Black Hole": "#3366CC",
        "Death Wave": "#109618",
        "Golden Bot": "#0099C6",
        "All overlap": "#990099",
        "Cumulative overlap %": "#FF9900",
    }
    for uw_name, series in timeline.active_by_uw.items():
        datasets.append(
            {
                "label": uw_name,
                "data": series,
                "borderColor": palette.get(uw_name, "#777777"),
                "backgroundColor": palette.get(uw_name, "#777777"),
                "stepped": True,
                "pointRadius": 0,
                "borderWidth": 2,
                "yAxisID": "y",
            }
        )

    datasets.append(
        {
            "label": "All overlap",
            "data": timeline.overlap_all,
            "borderColor": palette["All overlap"],
            "backgroundColor": palette["All overlap"],
            "stepped": True,
            "pointRadius": 0,
            "borderWidth": 2,
            "yAxisID": "y",
        }
    )
    datasets.append(
        {
            "label": "Cumulative overlap %",
            "data": timeline.overlap_percent_cumulative,
            "borderColor": palette["Cumulative overlap %"],
            "backgroundColor": palette["Cumulative overlap %"],
            "stepped": False,
            "pointRadius": 0,
            "borderWidth": 2,
            "yAxisID": "y2",
        }
    )

    overlap_percent_final = timeline.overlap_percent_cumulative[-1] if timeline.overlap_percent_cumulative else 0.0
    overlap_windows = _overlap_windows(timeline.labels, timeline.overlap_all)
    return UWSyncPayload(
        chart_data={
            "labels": timeline.labels,
            "datasets": datasets,
            "overlap_windows": overlap_windows,
        },
        summary={
            "horizon_seconds": timeline.horizon_seconds,
            "overlap_percent": overlap_percent_final,
            "includes_golden_bot": bool(golden_bot_timing is not None),
        },
    )


def _golden_bot_timing(*, player: Player) -> UWTiming | None:
    """Return Golden Bot timing derived from saved bot parameters when available.

    Args:
        player: Player used to look up Golden Bot parameter state.

    Returns:
        UWTiming when Golden Bot is unlocked and has parseable cooldown/duration;
        otherwise None.
    """

    bot = (
        PlayerBot.objects.filter(player=player, bot_slug="golden_bot")
        .select_related("bot_definition")
        .prefetch_related("parameters__parameter_definition")
        .first()
    )
    if bot is None or not bot.unlocked:
        return None

    params = list(bot.parameters.all())
    cooldown_raw = next(
        (
            p.effective_value_raw
            for p in params
            if p.parameter_definition is not None and p.parameter_definition.key == ParameterKey.COOLDOWN.value
        ),
        "",
    )
    duration_raw = next(
        (
            p.effective_value_raw
            for p in params
            if p.parameter_definition is not None and p.parameter_definition.key == ParameterKey.DURATION.value
        ),
        "",
    )
    cooldown = _extract_seconds(cooldown_raw)
    duration = _extract_seconds(duration_raw)
    if cooldown is None or duration is None:
        return None
    return UWTiming(name="Golden Bot", cooldown_seconds=cooldown, duration_seconds=duration)


def _overlap_windows(labels: list[str], overlap: list[int]) -> list[dict[str, str]]:
    """Return label-based overlap windows for UI band rendering.

    Args:
        labels: Timeline labels (e.g. "0s", "1s").
        overlap: 0/1 overlap signal aligned to labels.

    Returns:
        List of windows like {"start": "10s", "end": "25s"}.
    """

    windows: list[dict[str, str]] = []
    start_idx: int | None = None
    for idx, value in enumerate(overlap):
        if value and start_idx is None:
            start_idx = idx
        if (not value) and start_idx is not None:
            windows.append({"start": labels[start_idx], "end": labels[idx - 1]})
            start_idx = None
    if start_idx is not None and labels:
        windows.append({"start": labels[start_idx], "end": labels[-1]})
    return windows
