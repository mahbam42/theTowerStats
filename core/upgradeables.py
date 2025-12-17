"""Shared helpers for upgradeable-entity dashboards.

This module builds display-only view models for entities that have:
- an unlock state
- exactly three upgradeable parameters
- wiki-derived level tables (value + cost per level)

The resulting payloads are intentionally UI-oriented and do not attempt to
encode gameplay logic beyond level progression and basic value formatting.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from django.db.models import QuerySet

from definitions.models import UltimateWeaponDefinition, Unit
from player_state.economy import parse_cost_amount
from player_state.models import Player, PlayerUltimateWeapon, PlayerUltimateWeaponParameter


@dataclass(frozen=True, slots=True)
class ParameterLevelRow:
    """A single level-table row for client-side optimistic rendering."""

    level: int
    value_raw: str
    cost_raw: str


def _extract_number(value_raw: str) -> float | None:
    """Extract a best-effort float from a raw wiki string.

    Args:
        value_raw: Raw value string from wiki-derived tables.

    Returns:
        Parsed float when a numeric token is present, otherwise None.
    """

    match = re.search(r"([+-]?[0-9]+(?:\\.[0-9]+)?)", value_raw.replace(",", ""))
    if not match:
        return None
    try:
        return float(match.group(1))
    except ValueError:
        return None


def format_delta(*, current_raw: str | None, next_raw: str | None, unit_kind: str) -> str | None:
    """Format an emphasized delta for a value transition.

    Args:
        current_raw: Current raw value.
        next_raw: Next-level raw value.
        unit_kind: A `definitions.Unit.Kind` choice value.

    Returns:
        A short delta string like "+2", "−0.3s", "+5%", or "+0.10x", or None
        when values are not parseable.
    """

    if not current_raw or not next_raw:
        return None
    current_num = _extract_number(current_raw)
    next_num = _extract_number(next_raw)
    if current_num is None or next_num is None:
        return None

    delta = next_num - current_num
    if delta == 0:
        return None

    sign = "+" if delta > 0 else "−"
    magnitude = abs(delta)

    suffix = ""
    if unit_kind == Unit.Kind.SECONDS:
        suffix = "s"
    elif unit_kind == Unit.Kind.PERCENT:
        suffix = "%"
    elif unit_kind == Unit.Kind.MULTIPLIER:
        suffix = "x"

    display = f"{magnitude:g}{suffix}"
    return f"{sign}{display}"


def total_stones_invested_for_parameter(*, parameter_definition, level: int) -> int:
    """Return total stones invested for a parameter up to a selected level.

    Args:
        parameter_definition: An UltimateWeaponParameterDefinition-like object.
        level: Current selected level.

    Returns:
        Total parsed stone cost across level rows up to `level`.
    """

    if level <= 0:
        return 0
    total = 0
    for row in parameter_definition.levels.filter(level__lte=level):
        parsed = parse_cost_amount(cost_raw=getattr(row, "cost_raw", None))
        if parsed is not None:
            total += parsed
    return total


def build_uw_parameter_view(
    *,
    player_param: PlayerUltimateWeaponParameter,
    levels: list[ParameterLevelRow],
    unit_kind: str,
) -> dict[str, object]:
    """Build a template-ready parameter payload for the UW dashboard."""

    current_level = int(player_param.level or 0)
    max_level = max((row.level for row in levels), default=0)

    current_row = next((row for row in levels if row.level == current_level), None)
    if current_row is None and levels:
        current_row = levels[0]
        current_level = current_row.level

    next_row = next((row for row in levels if row.level == current_level + 1), None)
    is_maxed = current_level >= max_level and max_level > 0

    current_value_raw = current_row.value_raw if current_row else ""
    next_value_raw = next_row.value_raw if next_row else ""
    next_cost_raw = next_row.cost_raw if next_row else ""

    return {
        "id": player_param.id,
        "name": player_param.parameter_definition.display_name,
        "unit_kind": unit_kind,
        "level": current_level,
        "max_level": max_level,
        "current_value_raw": current_value_raw,
        "next_value_raw": next_value_raw,
        "next_cost_raw": next_cost_raw,
        "delta": format_delta(
            current_raw=current_value_raw,
            next_raw=next_value_raw,
            unit_kind=unit_kind,
        ),
        "is_maxed": is_maxed,
        "levels": [{"level": row.level, "value_raw": row.value_raw, "cost_raw": row.cost_raw} for row in levels],
    }


def validate_uw_parameter_definitions(*, uw_definition: UltimateWeaponDefinition) -> None:
    """Enforce that a UW has exactly three upgrade parameters.

    Args:
        uw_definition: UltimateWeaponDefinition to validate.

    Raises:
        ValueError: When the UW does not have exactly three parameter definitions.
    """

    count = uw_definition.parameter_definitions.count()
    if count != 3:
        raise ValueError(
            f"Ultimate weapon {uw_definition.slug!r} has {count} parameters; expected exactly 3."
        )


def ensure_player_uw_rows(
    *,
    player: Player,
    player_uws: QuerySet[PlayerUltimateWeapon],
    uw_definitions: list[UltimateWeaponDefinition],
) -> None:
    """Ensure the player has PlayerUltimateWeapon rows for all definitions.

    Args:
        player_uws: QuerySet filtered to the target player.
        uw_definitions: All UltimateWeaponDefinition rows to mirror.
    """

    existing = set(player_uws.values_list("ultimate_weapon_slug", flat=True))
    for uw_def in uw_definitions:
        if uw_def.slug in existing:
            continue
        PlayerUltimateWeapon.objects.create(
            player=player,
            ultimate_weapon_definition=uw_def,
            ultimate_weapon_slug=uw_def.slug,
            unlocked=False,
        )
