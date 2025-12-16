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
    coins: int | None,
    real_time_seconds: int | None,
    context: PlayerContextInput | None,
    entity_type: str | None,
    entity_name: str | None,
    config: MetricComputeConfig,
) -> tuple[float | None, tuple[UsedParameter, ...], tuple[str, ...]]:
    """Compute a metric value and return used parameters + assumptions.

    Args:
        metric_key: Metric key to compute.
        coins: Observed coins for the run.
        real_time_seconds: Observed duration seconds for the run.
        context: Optional player context + selected parameters.
        config: MetricComputeConfig.

    Returns:
        Tuple of (value, used_parameters, assumptions).
    """

    _ = (entity_type, config)

    if metric_key == "coins_per_hour":
        return (
            compute_observed_coins_per_hour(coins=coins, real_time_seconds=real_time_seconds),
            (),
            (),
        )

    if context is None:
        return None, (), ("Missing player context; derived metric not computed.",)

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
