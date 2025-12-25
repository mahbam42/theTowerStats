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
from core.upgradeables import format_delta
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
    unit_kind: str
    max_level: int
    current_level_display: int
    current_level_for_calc: int
    current_is_assumed: bool
    target_level: int | None
    notes: str
    is_completed: bool
    breakdown: GoalCostBreakdown | None
    target_options: tuple[dict[str, object], ...]


@dataclass(frozen=True, slots=True)
class GoalCandidate:
    """A selectable goal candidate for modal-based creation."""

    goal_type: str
    goal_key: str
    label: str
    currency: str
    max_level: int
    target_options: tuple[dict[str, object], ...]


def parse_goal_key(*, goal_key: str) -> tuple[str, str, str] | None:
    """Parse a goal key into (goal_type, entity_slug, parameter_key)."""

    parts = goal_key.split(":", 2)
    if len(parts) != 3:
        return None
    goal_type, entity_slug, parameter_key = (part.strip() for part in parts)
    if not goal_type or not entity_slug or not parameter_key:
        return None
    return goal_type, entity_slug, parameter_key


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


def _player_levels_by_definition_id(*, player, model) -> tuple[dict[int, int], set[int]]:
    """Return a map of parameter_definition_id -> player level plus known ids."""

    levels: dict[int, int] = {}
    known: set[int] = set()
    for definition_id, level in model.objects.filter(player=player, parameter_definition__isnull=False).values_list(
        "parameter_definition_id",
        "level",
    ):
        if definition_id is None:
            continue
        definition_id_int = int(definition_id)
        known.add(definition_id_int)
        levels[definition_id_int] = int(level or 0)
    return levels, known


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
    """Collect goal rows for the Goals dashboard, grouped by category.

    The Goals dashboard shows only active goals (stored GoalTarget rows). It does
    not list all possible parameters.
    """

    qs = GoalTarget.objects.filter(player=player)
    if goal_type:
        qs = qs.filter(goal_type=goal_type)
    grouped: dict[str, list[GoalRow]] = defaultdict(list)
    for target in qs.order_by("goal_type", "goal_key", "id"):
        row = goal_row_for_target(player=player, target=target)
        if row is None:
            continue
        if row.is_completed and not show_completed:
            continue
        grouped[row.goal_type].append(row)
    return {key: tuple(value) for key, value in grouped.items()}


def goals_widget_rows(*, player: Player, goal_type: str, limit: int = 3) -> tuple[GoalRow, ...]:
    """Return the top-N goal rows by remaining cost for a widget."""

    rows = [
        row
        for row in goal_rows_for_dashboard(player=player, goal_type=goal_type, show_completed=False).get(goal_type, ())
        if row.target_level is not None and row.breakdown is not None and row.breakdown.total_remaining > 0
    ]
    rows.sort(key=lambda r: (r.breakdown.total_remaining if r.breakdown else 0), reverse=True)
    return tuple(rows[:limit])


def goal_row_for_target(*, player: Player, target: GoalTarget) -> GoalRow | None:
    """Build a goal row for a stored GoalTarget."""

    parsed = parse_goal_key(goal_key=target.goal_key)
    if parsed is None:
        return None
    goal_type, entity_slug, parameter_key = parsed

    if goal_type == str(GoalType.BOT):
        return _bot_goal_row_for_target(
            player=player,
            target=target,
            entity_slug=entity_slug,
            parameter_key=parameter_key,
        )
    if goal_type == str(GoalType.GUARDIAN_CHIP):
        return _guardian_goal_row_for_target(
            player=player,
            target=target,
            entity_slug=entity_slug,
            parameter_key=parameter_key,
        )
    if goal_type == str(GoalType.ULTIMATE_WEAPON):
        return _uw_goal_row_for_target(
            player=player,
            target=target,
            entity_slug=entity_slug,
            parameter_key=parameter_key,
        )
    return None


def goal_candidates_for_modal(*, player: Player, goal_type: str | None = None) -> tuple[GoalCandidate, ...]:
    """Return selectable goal candidates for modal goal creation.

    Excludes goal keys that already exist for the player.
    """

    existing_keys = set(GoalTarget.objects.filter(player=player).values_list("goal_key", flat=True))
    candidates: list[GoalCandidate] = []

    if goal_type in (None, str(GoalType.BOT)):
        player_levels, known_definition_ids = _player_levels_by_definition_id(player=player, model=PlayerBotParameter)
        for param_def in (
            BotParameterDefinition.objects.select_related("bot_definition")
            .prefetch_related("levels")
            .order_by("bot_definition__name", "display_name")
        ):
            entity = param_def.bot_definition
            key = goal_key_for_parameter(
                goal_type=str(GoalType.BOT),
                entity_slug=str(entity.slug),
                parameter_key=str(param_def.key),
            )
            if key in existing_keys:
                continue
            levels = list(param_def.levels.order_by("level"))
            _costs_by_level, max_level, currency = _level_cost_rows(levels=levels)
            current_raw = player_levels.get(param_def.id, 0)
            current_known = param_def.id in known_definition_ids
            current_level_display = current_raw if current_known else 0
            options = target_options_relative_to_current_level(
                levels=levels,
                unit_kind=str(param_def.unit_kind or ""),
                current_level_display=current_level_display,
            )
            candidates.append(
                GoalCandidate(
                    goal_type=str(GoalType.BOT),
                    goal_key=key,
                    label=f"{entity.name} • {param_def.display_name}",
                    currency=currency_label(currency=currency),
                    max_level=max_level,
                    target_options=options,
                )
            )

    if goal_type in (None, str(GoalType.GUARDIAN_CHIP)):
        player_levels, known_definition_ids = _player_levels_by_definition_id(
            player=player, model=PlayerGuardianChipParameter
        )
        for param_def in (
            GuardianChipParameterDefinition.objects.select_related("guardian_chip_definition")
            .prefetch_related("levels")
            .order_by("guardian_chip_definition__name", "display_name")
        ):
            entity = param_def.guardian_chip_definition
            key = goal_key_for_parameter(
                goal_type=str(GoalType.GUARDIAN_CHIP),
                entity_slug=str(entity.slug),
                parameter_key=str(param_def.key),
            )
            if key in existing_keys:
                continue
            levels = list(param_def.levels.order_by("level"))
            _costs_by_level, max_level, currency = _level_cost_rows(levels=levels)
            current_raw = player_levels.get(param_def.id, 0)
            current_known = param_def.id in known_definition_ids
            current_level_display = current_raw if current_known else 1
            options = target_options_relative_to_current_level(
                levels=levels,
                unit_kind=str(param_def.unit_kind or ""),
                current_level_display=current_level_display,
            )
            candidates.append(
                GoalCandidate(
                    goal_type=str(GoalType.GUARDIAN_CHIP),
                    goal_key=key,
                    label=f"{entity.name} • {param_def.display_name}",
                    currency=currency_label(currency=currency),
                    max_level=max_level,
                    target_options=options,
                )
            )

    if goal_type in (None, str(GoalType.ULTIMATE_WEAPON)):
        player_levels, known_definition_ids = _player_levels_by_definition_id(
            player=player, model=PlayerUltimateWeaponParameter
        )
        for param_def in (
            UltimateWeaponParameterDefinition.objects.select_related("ultimate_weapon_definition")
            .prefetch_related("levels")
            .order_by("ultimate_weapon_definition__name", "display_name")
        ):
            entity = param_def.ultimate_weapon_definition
            key = goal_key_for_parameter(
                goal_type=str(GoalType.ULTIMATE_WEAPON),
                entity_slug=str(entity.slug),
                parameter_key=str(param_def.key),
            )
            if key in existing_keys:
                continue
            levels = list(param_def.levels.order_by("level"))
            _costs_by_level, max_level, currency = _level_cost_rows(levels=levels)
            current_raw = player_levels.get(param_def.id, 0)
            current_known = param_def.id in known_definition_ids
            current_level_display = current_raw if current_known else 1
            options = target_options_relative_to_current_level(
                levels=levels,
                unit_kind=str(param_def.unit_kind or ""),
                current_level_display=current_level_display,
            )
            candidates.append(
                GoalCandidate(
                    goal_type=str(GoalType.ULTIMATE_WEAPON),
                    goal_key=key,
                    label=f"{entity.name} • {param_def.display_name}",
                    currency=currency_label(currency=currency),
                    max_level=max_level,
                    target_options=options,
                )
            )

    return tuple(candidates)


def _target_options_for_levels(*, levels, unit_kind: str) -> tuple[dict[str, object], ...]:
    """Build target dropdown options (level, delta, cost) from wiki level rows.

    This produces step-to-step deltas and is kept for internal use. Most UI
    flows should prefer `target_options_relative_to_current_level`.
    """

    ordered = list(levels)
    prev_value_raw: str | None = None
    options: list[dict[str, object]] = []
    for row in ordered:
        next_value_raw = str(getattr(row, "value_raw", "") or "")
        delta_text = format_delta(
            current_raw=prev_value_raw,
            next_raw=next_value_raw,
            unit_kind=str(unit_kind or ""),
        )
        cost_raw = str(getattr(row, "cost_raw", "") or "")
        label_parts = [f"L{row.level}"]
        if delta_text is None and prev_value_raw is not None and next_value_raw:
            delta_text = "no change"
        if delta_text:
            label_parts.append(delta_text)
        if cost_raw:
            label_parts.append(f"cost {cost_raw}")
        options.append({"level": int(row.level), "label": " • ".join(label_parts), "cost_raw": cost_raw})
        prev_value_raw = next_value_raw
    return tuple(options)


def target_options_relative_to_current_level(
    *,
    levels,
    unit_kind: str,
    current_level_display: int,
) -> tuple[dict[str, object], ...]:
    """Build target dropdown options with delta relative to the current level.

    The delta shown is the change from the player's current displayed level to
    the selected target level, not the step-to-step increment.
    """

    ordered = list(levels)
    baseline_value_raw: str | None = None
    for row in ordered:
        if int(getattr(row, "level", 0)) == int(current_level_display):
            baseline_value_raw = str(getattr(row, "value_raw", "") or "")
            break

    options: list[dict[str, object]] = []
    for row in ordered:
        to_level = int(getattr(row, "level", 0))
        to_value_raw = str(getattr(row, "value_raw", "") or "")
        cost_raw = str(getattr(row, "cost_raw", "") or "")

        delta_text = None
        if baseline_value_raw is not None and to_value_raw:
            delta_text = format_delta(
                current_raw=baseline_value_raw,
                next_raw=to_value_raw,
                unit_kind=str(unit_kind or ""),
            )
            if delta_text is None:
                delta_text = "no change"
        else:
            delta_text = "Δ n/a"

        label_parts = [f"L{to_level}", delta_text]
        if cost_raw:
            label_parts.append(f"cost {cost_raw}")
        options.append({"level": to_level, "label": " • ".join(label_parts), "cost_raw": cost_raw})
    return tuple(options)


def _bot_goal_row_for_target(
    *, player: Player, target: GoalTarget, entity_slug: str, parameter_key: str
) -> GoalRow | None:
    """Build a goal row for a bot GoalTarget."""

    param_def = (
        BotParameterDefinition.objects.select_related("bot_definition")
        .prefetch_related("levels")
        .filter(bot_definition__slug=entity_slug, key=parameter_key)
        .first()
    )
    if param_def is None:
        return None
    entity = param_def.bot_definition

    player_levels, known_definition_ids = _player_levels_by_definition_id(player=player, model=PlayerBotParameter)
    current_raw = player_levels.get(param_def.id, 0)
    current_known = param_def.id in known_definition_ids
    current_level_display = current_raw if current_known else 0
    current_level_for_calc = current_raw if current_known else 0
    current_is_assumed = not current_known

    levels = list(param_def.levels.order_by("level"))
    costs_by_level, max_level, currency = _level_cost_rows(levels=levels)
    currency_text = currency_label(currency=currency)

    is_completed = bool(current_known and current_raw >= target.target_level)
    breakdown = compute_goal_cost_breakdown(
        costs_by_level=costs_by_level,
        currency=currency_text,
        current_level_display=current_level_display,
        current_level_for_calc=current_level_for_calc,
        current_is_assumed=current_is_assumed,
        target_level=int(target.target_level),
    )
    options = target_options_relative_to_current_level(
        levels=levels,
        unit_kind=str(param_def.unit_kind or ""),
        current_level_display=current_level_display,
    )

    return GoalRow(
        goal_type=str(GoalType.BOT),
        goal_key=target.goal_key,
        entity_name=str(entity.name),
        parameter_name=str(param_def.display_name),
        currency=currency_text,
        unit_kind=str(param_def.unit_kind or ""),
        max_level=max_level,
        current_level_display=current_level_display,
        current_level_for_calc=current_level_for_calc,
        current_is_assumed=current_is_assumed,
        target_level=int(target.target_level),
        notes=str(target.notes or ""),
        is_completed=is_completed,
        breakdown=breakdown,
        target_options=options,
    )


def _guardian_goal_row_for_target(
    *, player: Player, target: GoalTarget, entity_slug: str, parameter_key: str
) -> GoalRow | None:
    """Build a goal row for a guardian chip GoalTarget."""

    param_def = (
        GuardianChipParameterDefinition.objects.select_related("guardian_chip_definition")
        .prefetch_related("levels")
        .filter(guardian_chip_definition__slug=entity_slug, key=parameter_key)
        .first()
    )
    if param_def is None:
        return None
    entity = param_def.guardian_chip_definition

    player_levels, known_definition_ids = _player_levels_by_definition_id(
        player=player, model=PlayerGuardianChipParameter
    )
    current_raw = player_levels.get(param_def.id, 0)
    current_known = param_def.id in known_definition_ids
    current_level_display = current_raw if current_known else 1
    current_level_for_calc = current_raw if current_known else 0
    current_is_assumed = not current_known

    levels = list(param_def.levels.order_by("level"))
    costs_by_level, max_level, currency = _level_cost_rows(levels=levels)
    currency_text = currency_label(currency=currency)

    is_completed = bool(current_known and current_raw >= target.target_level)
    breakdown = compute_goal_cost_breakdown(
        costs_by_level=costs_by_level,
        currency=currency_text,
        current_level_display=current_level_display,
        current_level_for_calc=current_level_for_calc,
        current_is_assumed=current_is_assumed,
        target_level=int(target.target_level),
    )
    options = target_options_relative_to_current_level(
        levels=levels,
        unit_kind=str(param_def.unit_kind or ""),
        current_level_display=current_level_display,
    )

    return GoalRow(
        goal_type=str(GoalType.GUARDIAN_CHIP),
        goal_key=target.goal_key,
        entity_name=str(entity.name),
        parameter_name=str(param_def.display_name),
        currency=currency_text,
        unit_kind=str(param_def.unit_kind or ""),
        max_level=max_level,
        current_level_display=current_level_display,
        current_level_for_calc=current_level_for_calc,
        current_is_assumed=current_is_assumed,
        target_level=int(target.target_level),
        notes=str(target.notes or ""),
        is_completed=is_completed,
        breakdown=breakdown,
        target_options=options,
    )


def _uw_goal_row_for_target(
    *, player: Player, target: GoalTarget, entity_slug: str, parameter_key: str
) -> GoalRow | None:
    """Build a goal row for an ultimate weapon GoalTarget."""

    param_def = (
        UltimateWeaponParameterDefinition.objects.select_related("ultimate_weapon_definition")
        .prefetch_related("levels")
        .filter(ultimate_weapon_definition__slug=entity_slug, key=parameter_key)
        .first()
    )
    if param_def is None:
        return None
    entity = param_def.ultimate_weapon_definition

    player_levels, known_definition_ids = _player_levels_by_definition_id(
        player=player, model=PlayerUltimateWeaponParameter
    )
    current_raw = player_levels.get(param_def.id, 0)
    current_known = param_def.id in known_definition_ids
    current_level_display = current_raw if current_known else 1
    current_level_for_calc = current_raw if current_known else 0
    current_is_assumed = not current_known

    levels = list(param_def.levels.order_by("level"))
    costs_by_level, max_level, currency = _level_cost_rows(levels=levels)
    currency_text = currency_label(currency=currency)

    is_completed = bool(current_known and current_raw >= target.target_level)
    breakdown = compute_goal_cost_breakdown(
        costs_by_level=costs_by_level,
        currency=currency_text,
        current_level_display=current_level_display,
        current_level_for_calc=current_level_for_calc,
        current_is_assumed=current_is_assumed,
        target_level=int(target.target_level),
    )
    options = target_options_relative_to_current_level(
        levels=levels,
        unit_kind=str(param_def.unit_kind or ""),
        current_level_display=current_level_display,
    )

    return GoalRow(
        goal_type=str(GoalType.ULTIMATE_WEAPON),
        goal_key=target.goal_key,
        entity_name=str(entity.name),
        parameter_name=str(param_def.display_name),
        currency=currency_text,
        unit_kind=str(param_def.unit_kind or ""),
        max_level=max_level,
        current_level_display=current_level_display,
        current_level_for_calc=current_level_for_calc,
        current_is_assumed=current_is_assumed,
        target_level=int(target.target_level),
        notes=str(target.notes or ""),
        is_completed=is_completed,
        breakdown=breakdown,
        target_options=options,
    )
