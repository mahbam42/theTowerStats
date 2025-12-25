"""Goals dashboard helpers.

This module bridges wiki-derived parameter level tables, player parameter state,
and the pure analysis functions that compute per-level and total remaining
currency to reach a target.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from analysis.goals import GoalCostBreakdown, compute_goal_cost_breakdown
from definitions.models import (
    BotParameterDefinition,
    Currency,
    GuardianChipParameterDefinition,
    UltimateWeaponParameterDefinition,
)
from player_state.models import (
    GoalTarget,
    GoalType,
    Player,
    PlayerBotParameter,
    PlayerGuardianChipParameter,
    PlayerUltimateWeaponParameter,
)


@dataclass(frozen=True, slots=True)
class GoalRow:
    """A template-ready goal row for the Goals dashboard."""

    goal_type: str
    goal_key: str
    entity_name: str
    parameter_name: str
    currency: str
    max_level: int
    current_level_display: int
    current_level_for_calc: int
    current_is_assumed: bool
    target_level: int | None
    label: str
    notes: str
    is_completed: bool
    breakdown: GoalCostBreakdown | None


def currency_label(*, currency: str) -> str:
    """Normalize a currency choice to a UI label."""

    if currency == Currency.STONES:
        return "stones"
    if currency == Currency.MEDALS:
        return "medals"
    if currency == Currency.BITS:
        return "bits"
    return currency


def goal_key_for_parameter(*, goal_type: str, entity_slug: str, parameter_key: str) -> str:
    """Build a stable goal key from an entity slug and parameter key."""

    return f"{goal_type}:{entity_slug}:{parameter_key}"


def _player_levels_by_definition_id(*, player, model) -> dict[int, int]:
    """Return a map of parameter_definition_id -> current player level."""

    levels: dict[int, int] = {}
    for definition_id, level in model.objects.filter(player=player, parameter_definition__isnull=False).values_list(
        "parameter_definition_id",
        "level",
    ):
        if definition_id is None:
            continue
        levels[int(definition_id)] = int(level or 0)
    return levels


def _targets_by_key(*, player: Player, goal_type: str) -> dict[str, GoalTarget]:
    """Return a map of goal_key -> GoalTarget for a player and goal type."""

    return {
        target.goal_key: target
        for target in GoalTarget.objects.filter(player=player, goal_type=goal_type)
    }


def _level_cost_rows(*, levels) -> tuple[dict[int, str], int, str]:
    """Extract cost mapping, max level, and currency from prefetched levels."""

    costs_by_level: dict[int, str] = {}
    currency = ""
    max_level = 0
    for row in levels:
        costs_by_level[int(row.level)] = str(row.cost_raw or "")
        currency = str(getattr(row, "currency", "") or currency)
        max_level = max(max_level, int(row.level))
    return costs_by_level, max_level, currency


def goal_rows_for_dashboard(
    *, player: Player, goal_type: str | None, show_completed: bool
) -> dict[str, tuple[GoalRow, ...]]:
    """Collect goal rows for the Goals dashboard, grouped by category."""

    selected = (
        {goal_type}
        if goal_type
        else {
            str(GoalType.BOT),
            str(GoalType.GUARDIAN_CHIP),
            str(GoalType.ULTIMATE_WEAPON),
        }
    )
    grouped: dict[str, list[GoalRow]] = defaultdict(list)
    for selected_type in sorted(selected):
        rows = _goal_rows_for_type(player=player, goal_type=selected_type, show_completed=show_completed)
        grouped[selected_type].extend(rows)
    return {key: tuple(value) for key, value in grouped.items()}


def goals_widget_rows(*, player: Player, goal_type: str, limit: int = 3) -> tuple[GoalRow, ...]:
    """Return the top-N goal rows by remaining cost for a widget."""

    rows = [
        row
        for row in _goal_rows_for_type(player=player, goal_type=goal_type, show_completed=False)
        if row.target_level is not None and row.breakdown is not None and row.breakdown.total_remaining > 0
    ]
    rows.sort(key=lambda r: (r.breakdown.total_remaining if r.breakdown else 0), reverse=True)
    return tuple(rows[:limit])


def _goal_rows_for_type(*, player: Player, goal_type: str, show_completed: bool) -> list[GoalRow]:
    """Build goal rows for a single GoalType."""

    if goal_type == str(GoalType.BOT):
        return _bot_goal_rows(player=player, show_completed=show_completed)
    if goal_type == str(GoalType.GUARDIAN_CHIP):
        return _guardian_goal_rows(player=player, show_completed=show_completed)
    if goal_type == str(GoalType.ULTIMATE_WEAPON):
        return _uw_goal_rows(player=player, show_completed=show_completed)
    return []


def _bot_goal_rows(*, player: Player, show_completed: bool) -> list[GoalRow]:
    """Build goal rows for Bot parameter definitions."""

    player_levels = _player_levels_by_definition_id(player=player, model=PlayerBotParameter)
    targets = _targets_by_key(player=player, goal_type=str(GoalType.BOT))
    rows: list[GoalRow] = []
    for param_def in (
        BotParameterDefinition.objects.select_related("bot_definition").prefetch_related("levels").order_by(
            "bot_definition__name",
            "display_name",
        )
    ):
        entity = param_def.bot_definition
        goal_key = goal_key_for_parameter(
            goal_type=str(GoalType.BOT),
            entity_slug=str(entity.slug),
            parameter_key=str(param_def.key),
        )
        target = targets.get(goal_key)
        current_raw = player_levels.get(param_def.id, 0)
        current_known = current_raw > 0
        current_level_display = current_raw if current_known else 1
        current_level_for_calc = current_raw if current_known else 0
        current_is_assumed = not current_known

        levels = list(param_def.levels.all())
        costs_by_level, max_level, currency = _level_cost_rows(levels=levels)
        currency_text = currency_label(currency=currency)
        target_level = target.target_level if target else None

        is_completed = bool(target_level is not None and current_known and current_raw >= target_level)
        if is_completed and not show_completed:
            continue

        breakdown = (
            compute_goal_cost_breakdown(
                costs_by_from_level=costs_by_level,
                currency=currency_text,
                current_level_display=current_level_display,
                current_level_for_calc=current_level_for_calc,
                target_level=target_level,
            )
            if target_level is not None
            else None
        )

        rows.append(
            GoalRow(
                goal_type=str(GoalType.BOT),
                goal_key=goal_key,
                entity_name=str(entity.name),
                parameter_name=str(param_def.display_name),
                currency=currency_text,
                max_level=max_level,
                current_level_display=current_level_display,
                current_level_for_calc=current_level_for_calc,
                current_is_assumed=current_is_assumed,
                target_level=target_level,
                label=(target.label if target else ""),
                notes=(target.notes if target else ""),
                is_completed=is_completed,
                breakdown=breakdown,
            )
        )
    return rows


def _guardian_goal_rows(*, player: Player, show_completed: bool) -> list[GoalRow]:
    """Build goal rows for Guardian chip parameter definitions."""

    player_levels = _player_levels_by_definition_id(player=player, model=PlayerGuardianChipParameter)
    targets = _targets_by_key(player=player, goal_type=str(GoalType.GUARDIAN_CHIP))
    rows: list[GoalRow] = []
    for param_def in (
        GuardianChipParameterDefinition.objects.select_related("guardian_chip_definition")
        .prefetch_related("levels")
        .order_by("guardian_chip_definition__name", "display_name")
    ):
        entity = param_def.guardian_chip_definition
        goal_key = goal_key_for_parameter(
            goal_type=str(GoalType.GUARDIAN_CHIP),
            entity_slug=str(entity.slug),
            parameter_key=str(param_def.key),
        )
        target = targets.get(goal_key)
        current_raw = player_levels.get(param_def.id, 0)
        current_known = current_raw > 0
        current_level_display = current_raw if current_known else 1
        current_level_for_calc = current_raw if current_known else 0
        current_is_assumed = not current_known

        levels = list(param_def.levels.all())
        costs_by_level, max_level, currency = _level_cost_rows(levels=levels)
        currency_text = currency_label(currency=currency)
        target_level = target.target_level if target else None

        is_completed = bool(target_level is not None and current_known and current_raw >= target_level)
        if is_completed and not show_completed:
            continue

        breakdown = (
            compute_goal_cost_breakdown(
                costs_by_from_level=costs_by_level,
                currency=currency_text,
                current_level_display=current_level_display,
                current_level_for_calc=current_level_for_calc,
                target_level=target_level,
            )
            if target_level is not None
            else None
        )

        rows.append(
            GoalRow(
                goal_type=str(GoalType.GUARDIAN_CHIP),
                goal_key=goal_key,
                entity_name=str(entity.name),
                parameter_name=str(param_def.display_name),
                currency=currency_text,
                max_level=max_level,
                current_level_display=current_level_display,
                current_level_for_calc=current_level_for_calc,
                current_is_assumed=current_is_assumed,
                target_level=target_level,
                label=(target.label if target else ""),
                notes=(target.notes if target else ""),
                is_completed=is_completed,
                breakdown=breakdown,
            )
        )
    return rows


def _uw_goal_rows(*, player: Player, show_completed: bool) -> list[GoalRow]:
    """Build goal rows for Ultimate weapon parameter definitions."""

    player_levels = _player_levels_by_definition_id(player=player, model=PlayerUltimateWeaponParameter)
    targets = _targets_by_key(player=player, goal_type=str(GoalType.ULTIMATE_WEAPON))
    rows: list[GoalRow] = []
    for param_def in (
        UltimateWeaponParameterDefinition.objects.select_related("ultimate_weapon_definition")
        .prefetch_related("levels")
        .order_by("ultimate_weapon_definition__name", "display_name")
    ):
        entity = param_def.ultimate_weapon_definition
        goal_key = goal_key_for_parameter(
            goal_type=str(GoalType.ULTIMATE_WEAPON),
            entity_slug=str(entity.slug),
            parameter_key=str(param_def.key),
        )
        target = targets.get(goal_key)
        current_raw = player_levels.get(param_def.id, 0)
        current_known = current_raw > 0
        current_level_display = current_raw if current_known else 1
        current_level_for_calc = current_raw if current_known else 0
        current_is_assumed = not current_known

        levels = list(param_def.levels.all())
        costs_by_level, max_level, currency = _level_cost_rows(levels=levels)
        currency_text = currency_label(currency=currency)
        target_level = target.target_level if target else None

        is_completed = bool(target_level is not None and current_known and current_raw >= target_level)
        if is_completed and not show_completed:
            continue

        breakdown = (
            compute_goal_cost_breakdown(
                costs_by_from_level=costs_by_level,
                currency=currency_text,
                current_level_display=current_level_display,
                current_level_for_calc=current_level_for_calc,
                target_level=target_level,
            )
            if target_level is not None
            else None
        )

        rows.append(
            GoalRow(
                goal_type=str(GoalType.ULTIMATE_WEAPON),
                goal_key=goal_key,
                entity_name=str(entity.name),
                parameter_name=str(param_def.display_name),
                currency=currency_text,
                max_level=max_level,
                current_level_display=current_level_display,
                current_level_for_calc=current_level_for_calc,
                current_is_assumed=current_is_assumed,
                target_level=target_level,
                label=(target.label if target else ""),
                notes=(target.notes if target else ""),
                is_completed=is_completed,
                breakdown=breakdown,
            )
        )
    return rows
