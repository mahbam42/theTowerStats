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
from decimal import Decimal, InvalidOperation
from typing import Protocol, Sequence

from django.db.models import QuerySet

from definitions.models import ParameterKey, UltimateWeaponDefinition, Unit
from player_state.economy import parse_cost_amount
from player_state.models import Player, PlayerCard, PlayerUltimateWeapon, PlayerUltimateWeaponParameter

from core.modifier_explanations import collect_modifier_explanations


@dataclass(frozen=True, slots=True)
class ParameterLevelRow:
    """A single level-table row for client-side optimistic rendering."""

    level: int
    value_raw: str
    cost_raw: str


def _extract_decimal(value_raw: str) -> tuple[Decimal, int] | None:
    """Extract a best-effort Decimal and decimal-places count from a raw wiki string.

    Args:
        value_raw: Raw value string from wiki-derived tables.

    Returns:
        Tuple of (Decimal value, decimal_places) when a numeric token is present,
        otherwise None.
    """

    match = re.search(r"([+-]?[0-9]+(?:\.[0-9]+)?)", value_raw.replace(",", ""))
    if not match:
        return None
    token = match.group(1)
    decimal_places = 0
    if "." in token:
        decimal_places = len(token.split(".", 1)[1])
    try:
        return Decimal(token), decimal_places
    except (InvalidOperation, ValueError):
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
    current = _extract_decimal(current_raw)
    nxt = _extract_decimal(next_raw)
    if current is None or nxt is None:
        return None

    current_num, current_dp = current
    next_num, next_dp = nxt
    delta = next_num - current_num
    if delta == 0:
        return None

    sign = "+" if delta > 0 else "−"
    magnitude = abs(delta)
    display_dp = max(current_dp, next_dp)

    suffix = ""
    if unit_kind == Unit.Kind.SECONDS:
        suffix = "s"
    elif unit_kind == Unit.Kind.PERCENT:
        suffix = "%"
    elif unit_kind == Unit.Kind.MULTIPLIER:
        suffix = "x"

    if display_dp > 0:
        display_raw = f"{magnitude:.{display_dp}f}"
        display_trimmed = display_raw.rstrip("0").rstrip(".")
        display = f"{display_trimmed}{suffix}"
    else:
        display = f"{int(magnitude)}{suffix}"
    return f"{sign}{display}"


def _total_cost_invested_for_parameter(*, parameter_definition, level: int) -> int:
    """Return total parsed cost for a parameter up to a selected level.

    Args:
        parameter_definition: A parameter definition with `.levels` rows exposing `cost_raw`.
        level: Current selected level.

    Returns:
        Total parsed cost across level rows up to `level`.
    """

    if level <= 0:
        return 0
    total = 0
    for row in parameter_definition.levels.filter(level__lt=level):
        parsed = parse_cost_amount(cost_raw=getattr(row, "cost_raw", None))
        if parsed is not None:
            total += parsed
    return total


def total_currency_invested_for_parameter(*, parameter_definition, level: int) -> int:
    """Return total currency invested for a parameter up to a selected level.

    Args:
        parameter_definition: A parameter definition with `.levels` rows exposing `cost_raw`.
        level: Current selected level.

    Returns:
        Total parsed cost across level rows up to `level`.
    """

    return _total_cost_invested_for_parameter(parameter_definition=parameter_definition, level=level)


def total_stones_invested_for_parameter(*, parameter_definition, level: int) -> int:
    """Return total stones invested for a parameter up to a selected level.

    Args:
        parameter_definition: A parameter definition with `.levels` rows exposing `cost_raw`.
        level: Current selected level.

    Returns:
        Total parsed stone cost across level rows up to `level`.
    """

    return _total_cost_invested_for_parameter(parameter_definition=parameter_definition, level=level)


class _ParameterDefinitionLike(Protocol):
    display_name: str


class _PlayerParameterLike(Protocol):
    id: int
    level: int
    parameter_definition: _ParameterDefinitionLike
    effective_value_raw: str
    effective_notes: str


def build_upgradeable_parameter_view(
    *,
    player: Player,
    entity_kind: str,
    player_param: _PlayerParameterLike,
    levels: list[ParameterLevelRow],
    unit_kind: str,
    player_cards: Sequence[PlayerCard] = (),
) -> dict[str, object]:
    """Build a template-ready parameter payload for upgradeable dashboards.

    Args:
        player: Player owning the parameter.
        entity_kind: Entity kind used to scope the parameter key (e.g. "ultimate_weapon").
        player_param: Player-selected parameter instance.
        levels: Ordered level-table rows for optimistic client rendering.
        unit_kind: A `definitions.Unit.Kind` choice value.
        player_cards: Optional pre-fetched player cards (for best-effort explanations).

    Returns:
        Dictionary of values expected by the upgradeable dashboard template.
    """

    current_level = int(getattr(player_param, "level", 0) or 0)
    max_level = max((row.level for row in levels), default=0)
    min_level = levels[0].level if levels else 0

    current_row = next((row for row in levels if row.level == current_level), None)
    if current_row is None and levels:
        current_row = levels[0]
        current_level = current_row.level

    next_row = next((row for row in levels if row.level == current_level + 1), None)
    is_maxed = current_level >= max_level and max_level > 0
    is_min = current_level <= min_level

    base_value_raw = current_row.value_raw if current_row else ""
    next_value_raw = next_row.value_raw if next_row else ""
    next_cost_raw = current_row.cost_raw if (current_row and next_row) else ""

    raw_effective_override = (getattr(player_param, "effective_value_raw", "") or "").strip()
    effective_value_raw = raw_effective_override or base_value_raw

    scoped_key = getattr(getattr(player_param, "parameter_definition", None), "key", None)
    parameter_key = f"{entity_kind}.{scoped_key}" if scoped_key else f"{entity_kind}.unknown"
    explanations = collect_modifier_explanations(
        player=player,
        parameter_key=parameter_key,
        base_value_raw=base_value_raw,
        effective_value_raw=effective_value_raw,
        player_param=player_param,
        player_cards=player_cards,
    )

    return {
        "id": player_param.id,
        "name": player_param.parameter_definition.display_name,
        "unit_kind": unit_kind,
        "level": current_level,
        "min_level": min_level,
        "max_level": max_level,
        "base_value_raw": base_value_raw,
        "effective_value_raw": effective_value_raw,
        "modifier_explanations": [
            {
                "parameter_key": e.parameter_key,
                "source_type": e.source_type,
                "effect_type": e.effect_type,
                "description": e.description,
            }
            for e in explanations
        ],
        "current_value_raw": base_value_raw,
        "next_value_raw": next_value_raw,
        "next_cost_raw": next_cost_raw,
        "delta": format_delta(
            current_raw=base_value_raw,
            next_raw=next_value_raw,
            unit_kind=unit_kind,
        ),
        "is_min": is_min,
        "is_maxed": is_maxed,
        "levels": [{"level": row.level, "value_raw": row.value_raw, "cost_raw": row.cost_raw} for row in levels],
    }


def build_uw_parameter_view(
    *,
    player: Player,
    player_param: PlayerUltimateWeaponParameter,
    levels: list[ParameterLevelRow],
    unit_kind: str,
    player_cards: Sequence[PlayerCard] = (),
) -> dict[str, object]:
    """Build a template-ready parameter payload for the UW dashboard."""

    return build_upgradeable_parameter_view(
        player=player,
        entity_kind="ultimate_weapon",
        player_param=player_param,
        levels=levels,
        unit_kind=unit_kind,
        player_cards=player_cards,
    )


def validate_uw_parameter_definitions(*, uw_definition: UltimateWeaponDefinition) -> None:
    """Enforce that a UW has exactly three known upgrade parameters.

    Args:
        uw_definition: UltimateWeaponDefinition to validate.

    Raises:
        ValueError: When the UW does not have exactly three parameter definitions or
            contains keys not present in the ParameterKey registry.
    """

    validate_parameter_definitions(
        parameter_definitions=uw_definition.parameter_definitions,
        expected_count=3,
        entity_kind="ultimate weapon",
        entity_slug=uw_definition.slug,
    )


def validate_parameter_definitions(
    *,
    parameter_definitions,
    expected_count: int,
    entity_kind: str,
    entity_slug: str,
) -> None:
    """Enforce that an entity has exactly N known ParameterKey parameter definitions.

    Args:
        parameter_definitions: QuerySet-like collection of parameter definitions.
        expected_count: Required number of parameters for the entity.
        entity_kind: Display kind used in error messages (e.g. "guardian chip").
        entity_slug: Entity identifier used in error messages.

    Raises:
        ValueError: When the entity does not have exactly `expected_count` parameter definitions
            or contains keys not present in the ParameterKey registry.
    """

    allowed = {key.value for key in ParameterKey}
    keys = [getattr(param, "key", None) for param in parameter_definitions.all()]
    unknown = [key for key in keys if key not in allowed]
    if unknown:
        raise ValueError(f"{entity_kind.title()} {entity_slug!r} has unknown parameter keys: {unknown}.")

    count = len(keys)
    if count != expected_count:
        raise ValueError(
            f"{entity_kind.title()} {entity_slug!r} has {count} parameters; expected exactly {expected_count}."
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
