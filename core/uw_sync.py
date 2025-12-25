"""Build descriptive UW sync payloads for UI rendering."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol, cast

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

DEFAULT_DEATH_WAVE_DURATION_SECONDS = 1


class _LevelRowLike(Protocol):
    level: int
    value_raw: str


class _ParameterDefinitionLike(Protocol):
    levels: object


class _PlayerParameterLike(Protocol):
    level: int
    effective_value_raw: str
    parameter_definition: _ParameterDefinitionLike | None


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


def _effective_value_raw(player_param: _PlayerParameterLike | None) -> str:
    """Return the effective raw value for a player parameter.

    Prefers an explicit `effective_value_raw` override when present; otherwise
    returns the wiki-derived value for the selected level.

    Args:
        player_param: Player parameter row to extract an effective raw value from.

    Returns:
        Effective raw value string, or an empty string when unavailable.
    """

    if player_param is None:
        return ""

    raw_override = (getattr(player_param, "effective_value_raw", "") or "").strip()
    if raw_override:
        return raw_override

    param_def = getattr(player_param, "parameter_definition", None)
    if param_def is None:
        return ""

    levels_attr = getattr(param_def, "levels", None)
    if levels_attr is None or not hasattr(levels_attr, "all"):
        return ""

    levels = cast(list[_LevelRowLike], list(levels_attr.all()))
    if not levels:
        return ""

    selected_level = int(getattr(player_param, "level", 0) or 0)
    for row in levels:
        if int(getattr(row, "level", -1)) == selected_level:
            return str(getattr(row, "value_raw", "") or "")

    min_row = min(levels, key=lambda row: int(getattr(row, "level", 0)))
    return str(getattr(min_row, "value_raw", "") or "")


def build_uw_sync_payload(*, player: Player) -> UWSyncPayload | None:
    """Return a UW sync chart payload when required inputs are available.

    Args:
        player: Player used to look up Ultimate Weapon parameter state.

    Returns:
        UWSyncPayload when Golden Tower, Black Hole, and Death Wave are unlocked
        and have parseable timing values; otherwise None.

        Death Wave does not have a duration parameter in the game UI, and its
        on-map persistence depends on combat conditions. This chart therefore
        treats Death Wave as a 1-second activation marker instead of attempting
        to model its true active time.
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
            .prefetch_related("parameters__parameter_definition__levels")
            .first()
        )
        if uw is None or not uw.unlocked:
            return None
        uws.append((slug, display, uw))

    timings: list[UWTiming] = []
    for slug, display, uw in uws:
        params = list(uw.parameters.all())
        cooldown_param = next(
            (
                p
                for p in params
                if p.parameter_definition is not None and p.parameter_definition.key == ParameterKey.COOLDOWN.value
            ),
            None,
        )
        duration_param = next(
            (
                p
                for p in params
                if p.parameter_definition is not None and p.parameter_definition.key == ParameterKey.DURATION.value
            ),
            None,
        )

        cooldown_raw = _effective_value_raw(cast(_PlayerParameterLike | None, cooldown_param))
        duration_raw = _effective_value_raw(cast(_PlayerParameterLike | None, duration_param))
        cooldown = _extract_seconds(cooldown_raw)
        duration = _extract_seconds(duration_raw)
        if slug == "death_wave" and duration is None:
            duration = DEFAULT_DEATH_WAVE_DURATION_SECONDS
        if cooldown is None or duration is None:
            return None
        timings.append(UWTiming(name=display, cooldown_seconds=cooldown, duration_seconds=duration))

    golden_bot_timing = _golden_bot_timing(player=player)
    if golden_bot_timing is not None:
        timings.append(golden_bot_timing)

    timeline = compute_uw_sync_timeline(
        timings,
        overlap_excluded_names=frozenset({"Death Wave"}),
        max_horizon_seconds=1800,
        step_seconds=1,
    )

    palette = {
        "Golden Tower": "#DC3912",
        "Black Hole": "#3366CC",
        "Death Wave": "#109618",
        "Golden Bot": "#0099C6",
        "All overlap": "#990099",
        "Cumulative overlap %": "#FF9900",
    }

    overlap_percent_final = timeline.overlap_percent_cumulative[-1] if timeline.overlap_percent_cumulative else 0.0
    overlap_windows = _overlap_windows(timeline.labels, timeline.overlap_all)

    chart_labels = [name for _slug, name, _uw in uws]
    if golden_bot_timing is not None:
        chart_labels.append("Golden Bot")
    chart_labels.append("All overlap")
    bar_datasets = _build_bar_datasets(
        timeline=timeline,
        chart_labels=chart_labels,
        palette=palette,
    )
    return UWSyncPayload(
        chart_data={
            "chart_type": "bar",
            "labels": chart_labels,
            "datasets": bar_datasets,
            "overlap_windows": overlap_windows,
            "horizon_seconds": timeline.horizon_seconds,
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
        .prefetch_related("parameters__parameter_definition__levels")
        .first()
    )
    if bot is None or not bot.unlocked:
        return None

    params = list(bot.parameters.all())
    cooldown_param = next(
        (
            p
            for p in params
            if p.parameter_definition is not None and p.parameter_definition.key == ParameterKey.COOLDOWN.value
        ),
        None,
    )
    duration_param = next(
        (
            p
            for p in params
            if p.parameter_definition is not None and p.parameter_definition.key == ParameterKey.DURATION.value
        ),
        None,
    )
    cooldown_raw = _effective_value_raw(cast(_PlayerParameterLike | None, cooldown_param))
    duration_raw = _effective_value_raw(cast(_PlayerParameterLike | None, duration_param))
    cooldown = _extract_seconds(cooldown_raw)
    duration = _extract_seconds(duration_raw)
    if cooldown is None or duration is None:
        return None
    return UWTiming(name="Golden Bot", cooldown_seconds=cooldown, duration_seconds=duration)


def _build_bar_datasets(*, timeline, chart_labels: list[str], palette: dict[str, str]) -> list[dict[str, object]]:
    """Build Chart.js floating-bar datasets for the UW sync schedule view.

    Args:
        timeline: Computed sync timeline.
        chart_labels: Ordered y-axis categories (row labels).
        palette: Color palette mapping per label.

    Returns:
        List of Chart.js datasets using `{x: [start, end], y: label}` points.
    """

    datasets: list[dict[str, object]] = []
    for uw_name, series in timeline.active_by_uw.items():
        if uw_name not in chart_labels:
            continue
        windows = _signal_windows(series, horizon_seconds=timeline.horizon_seconds, step_seconds=1)
        points = [{"x": [start, end], "y": uw_name} for start, end in windows]
        datasets.append(
            {
                "label": uw_name,
                "data": points,
                "backgroundColor": palette.get(uw_name, "#777777"),
                "borderColor": palette.get(uw_name, "#777777"),
                "borderWidth": 1,
                "barThickness": 14,
            }
        )

    if "All overlap" in chart_labels:
        windows = _signal_windows(timeline.overlap_all, horizon_seconds=timeline.horizon_seconds, step_seconds=1)
        points = [{"x": [start, end], "y": "All overlap"} for start, end in windows]
        datasets.append(
            {
                "label": "All overlap",
                "data": points,
                "backgroundColor": palette.get("All overlap", "#990099"),
                "borderColor": palette.get("All overlap", "#990099"),
                "borderWidth": 1,
                "barThickness": 14,
            }
        )

    return datasets


def _signal_windows(signal: list[int], *, horizon_seconds: int, step_seconds: int) -> list[tuple[int, int]]:
    """Return half-open [start, end) windows for a 0/1 signal.

    Args:
        signal: 0/1 list aligned to a timeline.
        horizon_seconds: Total modeled horizon in seconds.
        step_seconds: Step size in seconds for timeline sampling.

    Returns:
        List of (start_seconds, end_seconds) windows, where end is exclusive.
    """

    windows: list[tuple[int, int]] = []
    start: int | None = None
    step = max(1, int(step_seconds))
    for idx, value in enumerate(signal):
        t = idx * step
        if t > horizon_seconds:
            break
        if value and start is None:
            start = t
        if (not value) and start is not None:
            windows.append((start, t))
            start = None
    if start is not None:
        windows.append((start, horizon_seconds + step))
    return windows


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
