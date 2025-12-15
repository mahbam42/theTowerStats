"""Metric registry and computation helpers for the Analysis Engine.

This module centralizes the set of chartable metrics (observed and derived) and
their labels/units so the UI can offer consistent selections.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Final

from .context import PlayerContextInput
from .derived import MonteCarloConfig
from .derived import apply_multiplier
from .derived import effective_cooldown_seconds
from .derived import monte_carlo_expected_multiplier_bernoulli
from .dto import MetricDefinition
from .dto import UsedParameter
from .quantity import UnitType
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
    "coins_per_hour_effective_multiplier": MetricDefinition(
        key="coins_per_hour_effective_multiplier",
        label="Coins/hour (effective multiplier)",
        unit="coins/hour",
        kind="derived",
    ),
    "coins_per_hour_ev_simulated": MetricDefinition(
        key="coins_per_hour_ev_simulated",
        label="Coins/hour (EV, simulated)",
        unit="coins/hour",
        kind="derived",
    ),
    "effective_cooldown_seconds": MetricDefinition(
        key="effective_cooldown_seconds",
        label="Effective cooldown",
        unit="seconds",
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

    observed = compute_observed_coins_per_hour(coins=coins, real_time_seconds=real_time_seconds)
    if metric_key == "coins_per_hour":
        return observed, (), ()

    if context is None:
        return None, (), ("Missing player context; derived metric not computed.",)

    if metric_key == "coins_per_hour_effective_multiplier":
        multiplier, used = _effective_multiplier_from_context(context)
        value = apply_multiplier(observed, multiplier=multiplier)
        assumptions = (
            "Applies selected multipliers multiplicatively to observed coins/hour.",
            "This is a numerical implication of parameters, not a recommendation.",
        )
        return value, used, assumptions

    if metric_key == "coins_per_hour_ev_simulated":
        config_mc = config.monte_carlo or MonteCarloConfig(trials=1_000, seed=1337)
        multiplier, used = _ev_multiplier_simulated_from_context(context, config=config_mc)
        value = apply_multiplier(observed, multiplier=multiplier)
        assumptions = (
            f"Monte Carlo EV with trials={config_mc.trials} seed={config_mc.seed}.",
            "Proc modeled as independent Bernoulli trials.",
        )
        return value, used, assumptions

    if metric_key == "effective_cooldown_seconds":
        base_seconds, reductions, used = _cooldown_inputs_from_context(context)
        value = effective_cooldown_seconds(
            base_seconds=base_seconds, reduction_fractions=reductions
        )
        assumptions = (
            "effective = base * (1 - sum(reductions)) (clamped to >= 0).",
            "Base cooldown chosen from the first unlocked ultimate weapon with a base cooldown parameter.",
        )
        return value, used, assumptions

    return None, (), ("Unknown metric key; no value computed.",)


def _float_or_none(value: Decimal | None) -> float | None:
    """Convert a Decimal to float, returning None when missing."""

    if value is None:
        return None
    return float(value)


def _interpret_multiplier_param(raw_key: str, *, parsed_value: Decimal | None) -> float | None:
    """Interpret a parsed multiplier-like parameter into a multiplier factor.

    Rules:
    - Percent strings are parsed as fractional multipliers (e.g. 15% -> 0.15);
      treat those as additive: multiplier = 1 + fraction.
    - x-prefixed strings are parsed as multiplier factors directly (e.g. x1.15 -> 1.15).
    - Otherwise, treat parsed numeric values as multiplier factors when plausible.
    """

    if parsed_value is None:
        return None
    lowered = raw_key.casefold()
    if "percent" in lowered or lowered.endswith("_pct") or lowered.endswith("_percent"):
        return 1.0 + float(parsed_value)
    return float(parsed_value)


def _effective_multiplier_from_context(context: PlayerContextInput) -> tuple[float | None, tuple[UsedParameter, ...]]:
    """Compute a combined multiplicative factor from selected context parameters."""

    used: list[UsedParameter] = []
    product = 1.0
    found_any = False

    for card in context.cards:
        if not card.owned:
            continue
        for param in card.parameters + card.level_parameters:
            if param.parsed.unit_type is not UnitType.multiplier:
                continue
            if param.key not in {"coins_multiplier", "coins_bonus_percent"}:
                continue
            multiplier = _interpret_multiplier_param(param.key, parsed_value=param.parsed.normalized_value)
            used.append(
                UsedParameter(
                    entity_type="card",
                    entity_name=card.name,
                    key=param.key,
                    raw_value=param.raw_value,
                    normalized_value=_float_or_none(param.parsed.normalized_value),
                    wiki_revision_id=param.wiki_revision_id,
                )
            )
            if multiplier is None:
                continue
            product *= multiplier
            found_any = True

    if not found_any:
        return None, tuple(used)
    return product, tuple(used)


def _ev_multiplier_simulated_from_context(
    context: PlayerContextInput,
    *,
    config: MonteCarloConfig,
) -> tuple[float | None, tuple[UsedParameter, ...]]:
    """Compute a Monte Carlo expected multiplier from proc parameters."""

    used: list[UsedParameter] = []

    proc_chance: float | None = None
    proc_multiplier: float | None = None

    for card in context.cards:
        if not card.owned:
            continue
        for param in card.parameters + card.level_parameters:
            if param.key == "proc_chance":
                proc_chance = _float_or_none(param.parsed.normalized_value)
                used.append(
                    UsedParameter(
                        entity_type="card",
                        entity_name=card.name,
                        key=param.key,
                        raw_value=param.raw_value,
                        normalized_value=_float_or_none(param.parsed.normalized_value),
                        wiki_revision_id=param.wiki_revision_id,
                    )
                )
            if param.key == "proc_multiplier":
                proc_multiplier = _float_or_none(param.parsed.normalized_value)
                used.append(
                    UsedParameter(
                        entity_type="card",
                        entity_name=card.name,
                        key=param.key,
                        raw_value=param.raw_value,
                        normalized_value=_float_or_none(param.parsed.normalized_value),
                        wiki_revision_id=param.wiki_revision_id,
                    )
                )

    multiplier = monte_carlo_expected_multiplier_bernoulli(
        proc_chance=proc_chance,
        proc_multiplier=proc_multiplier,
        config=config,
    )
    return multiplier, tuple(used)


def _cooldown_inputs_from_context(
    context: PlayerContextInput,
) -> tuple[float | None, tuple[float, ...], tuple[UsedParameter, ...]]:
    """Extract cooldown inputs from context parameters.

    Base cooldown: first unlocked ultimate weapon with a `base_cooldown_seconds` parameter.
    Reductions: sum of any `cooldown_reduction_percent` multiplier-like parameters from owned cards.
    """

    used: list[UsedParameter] = []

    base_seconds: float | None = None
    for uw in sorted(context.ultimate_weapons, key=lambda u: u.name.casefold()):
        if not uw.unlocked:
            continue
        for param in uw.parameters:
            if param.key != "base_cooldown_seconds":
                continue
            base_seconds = _float_or_none(param.parsed.normalized_value)
            used.append(
                UsedParameter(
                    entity_type="ultimate_weapon",
                    entity_name=uw.name,
                    key=param.key,
                    raw_value=param.raw_value,
                    normalized_value=_float_or_none(param.parsed.normalized_value),
                    wiki_revision_id=param.wiki_revision_id,
                )
            )
            break
        if base_seconds is not None:
            break

    reductions: list[float] = []
    for card in context.cards:
        if not card.owned:
            continue
        for param in card.parameters + card.level_parameters:
            if param.key != "cooldown_reduction_percent":
                continue
            value = _float_or_none(param.parsed.normalized_value)
            used.append(
                UsedParameter(
                    entity_type="card",
                    entity_name=card.name,
                    key=param.key,
                    raw_value=param.raw_value,
                    normalized_value=value,
                    wiki_revision_id=param.wiki_revision_id,
                )
            )
            if value is None:
                continue
            reductions.append(value)

    return base_seconds, tuple(reductions), tuple(used)

