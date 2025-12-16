"""Metric registry and computation helpers for the Analysis Engine.

This module centralizes the set of chartable metrics (observed and derived) and
their labels/units so the UI can offer consistent selections.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from .context import ParameterInput, PlayerContextInput
from .derived import MonteCarloConfig
from .effects import activations_per_minute_from_parameters
from .effects import effective_cooldown_seconds_from_parameters
from .effects import uptime_percent_from_parameters
from .dto import MetricDefinition
from .dto import UsedParameter
from .rates import coins_per_hour


@dataclass(frozen=True, slots=True)
class MetricComputeConfig:
    """Configuration for metric computations.

    Args:
        monte_carlo: Optional MonteCarloConfig for metrics that use simulation.
    """

    monte_carlo: MonteCarloConfig | None = None


METRICS: Final[dict[str, MetricDefinition]] = {
    "coins_earned": MetricDefinition(
        key="coins_earned",
        label="Coins earned",
        unit="coins",
        kind="observed",
    ),
    "cash_earned": MetricDefinition(
        key="cash_earned",
        label="Cash earned",
        unit="cash",
        kind="observed",
    ),
    "cells_earned": MetricDefinition(
        key="cells_earned",
        label="Cells earned",
        unit="cells",
        kind="observed",
    ),
    "reroll_shards_earned": MetricDefinition(
        key="reroll_shards_earned",
        label="Reroll shards earned",
        unit="shards",
        kind="observed",
    ),
    "reroll_dice_earned": MetricDefinition(
        key="reroll_dice_earned",
        label="Reroll dice earned",
        unit="shards",
        kind="observed",
    ),
    "waves_reached": MetricDefinition(
        key="waves_reached",
        label="Waves reached",
        unit="waves",
        kind="observed",
    ),
    "coins_per_wave": MetricDefinition(
        key="coins_per_wave",
        label="Coins per wave",
        unit="coins/wave",
        kind="derived",
    ),
    "uw_runs_count": MetricDefinition(
        key="uw_runs_count",
        label="Runs using selected ultimate weapon",
        unit="runs",
        kind="observed",
    ),
    "guardian_runs_count": MetricDefinition(
        key="guardian_runs_count",
        label="Runs using selected guardian chip",
        unit="runs",
        kind="observed",
    ),
    "bot_runs_count": MetricDefinition(
        key="bot_runs_count",
        label="Runs using selected bot",
        unit="runs",
        kind="observed",
    ),
    "coins_per_hour": MetricDefinition(
        key="coins_per_hour",
        label="Coins/hour",
        unit="coins/hour",
        kind="observed",
    ),
    "uw_uptime_percent": MetricDefinition(
        key="uw_uptime_percent",
        label="Ultimate Weapon uptime",
        unit="percent",
        kind="derived",
    ),
    "guardian_activations_per_minute": MetricDefinition(
        key="guardian_activations_per_minute",
        label="Guardian activations/minute",
        unit="activations/min",
        kind="derived",
    ),
    "uw_effective_cooldown_seconds": MetricDefinition(
        key="uw_effective_cooldown_seconds",
        label="Ultimate Weapon effective cooldown",
        unit="seconds",
        kind="derived",
    ),
    "cooldown_reduction_effective": MetricDefinition(
        key="cooldown_reduction_effective",
        label="Effective cooldown",
        unit="seconds",
        kind="derived",
    ),
    "bot_uptime_percent": MetricDefinition(
        key="bot_uptime_percent",
        label="Bot uptime",
        unit="percent",
        kind="derived",
    ),
}


def list_metric_definitions() -> tuple[MetricDefinition, ...]:
    """Return the available metric definitions in a stable order."""

    return tuple(METRICS[key] for key in sorted(METRICS.keys()))


def get_metric_definition(metric_key: str) -> MetricDefinition:
    """Return a MetricDefinition for a key, defaulting to observed coins/hour."""

    return METRICS.get(metric_key) or METRICS["coins_per_hour"]


def compute_observed_coins_per_hour(*, coins: int | None, real_time_seconds: int | None) -> float | None:
    """Compute observed coins/hour from raw run fields."""

    if coins is None or real_time_seconds is None:
        return None
    return coins_per_hour(coins=coins, real_time_seconds=real_time_seconds)


def compute_metric_value(
    metric_key: str,
    *,
    record: object,
    coins: int | None,
    cash: int | None,
    cells: int | None,
    reroll_shards: int | None,
    wave: int | None,
    real_time_seconds: int | None,
    context: PlayerContextInput | None,
    entity_type: str | None,
    entity_name: str | None,
    config: MetricComputeConfig,
) -> tuple[float | None, tuple[UsedParameter, ...], tuple[str, ...]]:
    """Compute a metric value and return used parameters + assumptions.

    Args:
        metric_key: Metric key to compute.
        record: Run-like object used for relationship-based metrics (e.g. usage presence).
        coins: Observed coins for the run.
        cash: Observed cash for the run.
        cells: Observed cells for the run.
        reroll_shards: Observed reroll shards for the run.
        wave: Observed wave reached for the run.
        real_time_seconds: Observed duration seconds for the run.
        context: Optional player context + selected parameters.
        entity_type: Optional entity category for entity-scoped derived metrics.
        entity_name: Optional entity name for entity-scoped derived metrics.
        config: MetricComputeConfig.

    Returns:
        Tuple of (value, used_parameters, assumptions).
    """

    _ = config

    if metric_key == "coins_earned":
        return (float(coins) if coins is not None else None, (), ())

    if metric_key == "cash_earned":
        return (float(cash) if cash is not None else None, (), ())

    if metric_key == "cells_earned":
        return (float(cells) if cells is not None else None, (), ())

    if metric_key in ("reroll_shards_earned", "reroll_dice_earned"):
        return (float(reroll_shards) if reroll_shards is not None else None, (), ())

    if metric_key == "waves_reached":
        return (float(wave) if wave is not None else None, (), ())

    if metric_key == "coins_per_wave":
        if coins is None or wave is None or wave <= 0:
            return None, (), ()
        return float(coins) / float(wave), (), ("coins_per_wave = coins_earned / waves_reached.",)

    if metric_key == "uw_runs_count":
        if not entity_name:
            return None, (), ("Select an Ultimate Weapon to chart usage counts.",)
        related = getattr(record, "run_combat_uws", None)
        if related is None:
            return None, (), ()
        for row in getattr(related, "all", lambda: related)():
            uw_def = getattr(row, "ultimate_weapon_definition", None)
            if getattr(uw_def, "name", None) == entity_name:
                return 1.0, (), ()
        return 0.0, (), ()

    if metric_key == "guardian_runs_count":
        if not entity_name:
            return None, (), ("Select a Guardian Chip to chart usage counts.",)
        related = getattr(record, "run_guardians", None)
        if related is None:
            return None, (), ()
        for row in getattr(related, "all", lambda: related)():
            chip_def = getattr(row, "guardian_chip_definition", None)
            if getattr(chip_def, "name", None) == entity_name:
                return 1.0, (), ()
        return 0.0, (), ()

    if metric_key == "bot_runs_count":
        if not entity_name:
            return None, (), ("Select a Bot to chart usage counts.",)
        related = getattr(record, "run_bots", None)
        if related is None:
            return None, (), ()
        for row in getattr(related, "all", lambda: related)():
            bot_def = getattr(row, "bot_definition", None)
            if getattr(bot_def, "name", None) == entity_name:
                return 1.0, (), ()
        return 0.0, (), ()

    if metric_key == "coins_per_hour":
        return (
            compute_observed_coins_per_hour(coins=coins, real_time_seconds=real_time_seconds),
            (),
            (),
        )

    if context is None:
        return None, (), ("Missing player context; derived metric not computed.",)

    if metric_key == "cooldown_reduction_effective":
        if entity_type not in ("ultimate_weapon", "guardian_chip", "bot"):
            return None, (), ("Select an entity type to compute effective cooldown.",)
        params = _entity_parameters(context, entity_type=entity_type, entity_name=entity_name)
        if params is None:
            return None, (), ("Select an entity to compute effective cooldown.",)
        effect = effective_cooldown_seconds_from_parameters(
            entity_type=entity_type,
            entity_name=entity_name or "Unknown",
            parameters=params,
        )
        assumptions = (
            "effective_cooldown_seconds = cooldown_seconds.",
            "Uses the selected entity's Cooldown parameter.",
        )
        return effect.value, effect.used_parameters, assumptions

    if metric_key == "uw_uptime_percent":
        params = _entity_parameters(context, entity_type="ultimate_weapon", entity_name=entity_name)
        if params is None:
            return None, (), ("Select an Ultimate Weapon to compute uptime.",)
        effect = uptime_percent_from_parameters(
            entity_type="ultimate_weapon",
            entity_name=entity_name or "Unknown",
            parameters=params,
        )
        assumptions = (
            "uptime% = 100 * clamp(duration / cooldown, 0..1).",
            "Uses the selected Ultimate Weapon's Duration and Cooldown parameters.",
        )
        return effect.value, effect.used_parameters, assumptions

    if metric_key == "guardian_activations_per_minute":
        params = _entity_parameters(context, entity_type="guardian_chip", entity_name=entity_name)
        if params is None:
            return None, (), ("Select a Guardian Chip to compute activations/minute.",)
        effect = activations_per_minute_from_parameters(
            entity_type="guardian_chip",
            entity_name=entity_name or "Unknown",
            parameters=params,
        )
        assumptions = (
            "activations/min = 60 / cooldown_seconds.",
            "Uses the selected Guardian Chip's Cooldown parameter.",
        )
        return effect.value, effect.used_parameters, assumptions

    if metric_key == "uw_effective_cooldown_seconds":
        params = _entity_parameters(context, entity_type="ultimate_weapon", entity_name=entity_name)
        if params is None:
            return None, (), ("Select an Ultimate Weapon to compute effective cooldown.",)
        effect = effective_cooldown_seconds_from_parameters(
            entity_type="ultimate_weapon",
            entity_name=entity_name or "Unknown",
            parameters=params,
        )
        assumptions = (
            "effective_cooldown_seconds = cooldown_seconds.",
            "Uses the selected Ultimate Weapon's Cooldown parameter.",
        )
        return effect.value, effect.used_parameters, assumptions

    if metric_key == "bot_uptime_percent":
        params = _entity_parameters(context, entity_type="bot", entity_name=entity_name)
        if params is None:
            return None, (), ("Select a Bot to compute uptime.",)
        effect = uptime_percent_from_parameters(
            entity_type="bot",
            entity_name=entity_name or "Unknown",
            parameters=params,
        )
        assumptions = (
            "uptime% = 100 * clamp(duration / cooldown, 0..1).",
            "Uses the selected Bot's Duration and Cooldown parameters.",
        )
        return effect.value, effect.used_parameters, assumptions

    return None, (), ("Unknown metric key; no value computed.",)


def _entity_parameters(
    context: PlayerContextInput,
    *,
    entity_type: str,
    entity_name: str | None,
) -> tuple[ParameterInput, ...] | None:
    """Return parameters for a specific entity selection, or None when missing.

    Args:
        context: PlayerContextInput containing unlocked/owned entities.
        entity_type: One of "ultimate_weapon", "guardian_chip", "bot".
        entity_name: Display name to match against context entries.

    Returns:
        Tuple of ParameterInput entries, or None when selection/context is missing.
    """

    if not entity_name:
        return None

    if entity_type == "ultimate_weapon":
        for uw in context.ultimate_weapons:
            if uw.name == entity_name and uw.unlocked:
                return uw.parameters
        return None

    if entity_type == "guardian_chip":
        for chip in context.guardian_chips:
            if chip.name == entity_name and chip.owned:
                return chip.parameters
        return None

    if entity_type == "bot":
        for bot in context.bots:
            if bot.name == entity_name and bot.unlocked:
                return bot.parameters
        return None

    return None
