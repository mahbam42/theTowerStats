"""Metric registry and computation helpers for the Analysis Engine.

This module centralizes the set of chartable metrics (observed and derived) and
their labels/units so the UI can offer consistent selections.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from .raw_text_metrics import RAW_TEXT_METRIC_SPECS
from .uw_usage import is_ultimate_weapon_observed_active
from .categories import MetricCategory
from .context import ParameterInput, PlayerContextInput
from .derived import MonteCarloConfig
from .effects import activations_per_minute_from_parameters
from .effects import effective_cooldown_seconds_from_parameters
from .effects import uptime_percent_from_parameters
from .dto import MetricDefinition
from .dto import UsedParameter
from .rates import coins_per_hour
from .series_registry import DEFAULT_REGISTRY


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
        category=MetricCategory.economy,
        kind="observed",
    ),
    "cash_earned": MetricDefinition(
        key="cash_earned",
        label="Cash earned",
        unit="cash",
        category=MetricCategory.economy,
        kind="observed",
    ),
    "interest_earned": MetricDefinition(
        key="interest_earned",
        label="Interest earned",
        unit="cash",
        category=MetricCategory.economy,
        kind="observed",
    ),
    "cells_earned": MetricDefinition(
        key="cells_earned",
        label="Cells earned",
        unit="cells",
        category=MetricCategory.economy,
        kind="observed",
    ),
    "reroll_shards_earned": MetricDefinition(
        key="reroll_shards_earned",
        label="Reroll shards earned",
        unit="shards",
        category=MetricCategory.economy,
        kind="observed",
    ),
    "reroll_dice_earned": MetricDefinition(
        key="reroll_dice_earned",
        label="Reroll dice earned",
        unit="shards",
        category=MetricCategory.economy,
        kind="observed",
    ),
    "waves_reached": MetricDefinition(
        key="waves_reached",
        label="Waves reached",
        unit="waves",
        category=MetricCategory.utility,
        kind="observed",
    ),
    "coins_per_wave": MetricDefinition(
        key="coins_per_wave",
        label="Coins per wave",
        unit="coins/wave",
        category=MetricCategory.economy,
        kind="derived",
    ),
    "uw_runs_count": MetricDefinition(
        key="uw_runs_count",
        label="Runs using selected ultimate weapon",
        unit="runs",
        category=MetricCategory.utility,
        kind="observed",
    ),
    "guardian_runs_count": MetricDefinition(
        key="guardian_runs_count",
        label="Runs using selected guardian chip",
        unit="runs",
        category=MetricCategory.utility,
        kind="observed",
    ),
    "bot_runs_count": MetricDefinition(
        key="bot_runs_count",
        label="Runs using selected bot",
        unit="runs",
        category=MetricCategory.utility,
        kind="observed",
    ),
    "coins_per_hour": MetricDefinition(
        key="coins_per_hour",
        label="Coins/hour",
        unit="coins/hour",
        category=MetricCategory.efficiency,
        kind="observed",
    ),
    "waves_per_hour": MetricDefinition(
        key="waves_per_hour",
        label="Waves/hour",
        unit="waves/hour",
        category=MetricCategory.efficiency,
        kind="derived",
    ),
    "enemies_destroyed_per_hour": MetricDefinition(
        key="enemies_destroyed_per_hour",
        label="Enemies destroyed/hour",
        unit="enemies/hour",
        category=MetricCategory.efficiency,
        kind="derived",
    ),
    "coins_from_death_wave": MetricDefinition(
        key="coins_from_death_wave",
        label="Coins From Death Wave",
        unit="coins",
        category=MetricCategory.economy,
        kind="observed",
    ),
    "coins_from_golden_tower": MetricDefinition(
        key="coins_from_golden_tower",
        label="Coins From Golden Tower",
        unit="coins",
        category=MetricCategory.economy,
        kind="observed",
    ),
    "cash_from_golden_tower": MetricDefinition(
        key="cash_from_golden_tower",
        label="Cash From Golden Tower",
        unit="cash",
        category=MetricCategory.economy,
        kind="observed",
    ),
    "cash_from_other_sources": MetricDefinition(
        key="cash_from_other_sources",
        label="Other cash",
        unit="cash",
        category=MetricCategory.economy,
        kind="derived",
    ),
    "coins_from_black_hole": MetricDefinition(
        key="coins_from_black_hole",
        label="Coins From Black Hole",
        unit="coins",
        category=MetricCategory.economy,
        kind="observed",
    ),
    "coins_from_spotlight": MetricDefinition(
        key="coins_from_spotlight",
        label="Coins From Spotlight",
        unit="coins",
        category=MetricCategory.economy,
        kind="observed",
    ),
    "coins_from_orb": MetricDefinition(
        key="coins_from_orb",
        label="Coins From Orb",
        unit="coins",
        category=MetricCategory.economy,
        kind="observed",
    ),
    "coins_from_coin_upgrade": MetricDefinition(
        key="coins_from_coin_upgrade",
        label="Coins from Coin Upgrade",
        unit="coins",
        category=MetricCategory.economy,
        kind="observed",
    ),
    "coins_from_coin_bonuses": MetricDefinition(
        key="coins_from_coin_bonuses",
        label="Coins from Coin Bonuses",
        unit="coins",
        category=MetricCategory.economy,
        kind="observed",
    ),
    "coins_from_other_sources": MetricDefinition(
        key="coins_from_other_sources",
        label="Other coins",
        unit="coins",
        category=MetricCategory.economy,
        kind="observed",
    ),
    "guardian_damage": MetricDefinition(
        key="guardian_damage",
        label="Guardian Damage",
        unit="damage",
        category=MetricCategory.combat,
        kind="observed",
    ),
    "damage_dealt": MetricDefinition(
        key="damage_dealt",
        label="Damage dealt",
        unit="damage",
        category=MetricCategory.damage,
        kind="observed",
    ),
    "projectiles_damage": MetricDefinition(
        key="projectiles_damage",
        label="Projectiles Damage",
        unit="damage",
        category=MetricCategory.damage,
        kind="observed",
    ),
    "thorn_damage": MetricDefinition(
        key="thorn_damage",
        label="Thorn Damage",
        unit="damage",
        category=MetricCategory.damage,
        kind="observed",
    ),
    "orb_damage": MetricDefinition(
        key="orb_damage",
        label="Orb Damage",
        unit="damage",
        category=MetricCategory.damage,
        kind="observed",
    ),
    "land_mine_damage": MetricDefinition(
        key="land_mine_damage",
        label="Land Mine Damage",
        unit="damage",
        category=MetricCategory.damage,
        kind="observed",
    ),
    "inner_land_mine_damage": MetricDefinition(
        key="inner_land_mine_damage",
        label="Inner Land Mine Damage",
        unit="damage",
        category=MetricCategory.damage,
        kind="observed",
    ),
    "chain_lightning_damage": MetricDefinition(
        key="chain_lightning_damage",
        label="Chain Lightning Damage",
        unit="damage",
        category=MetricCategory.damage,
        kind="observed",
    ),
    "death_wave_damage": MetricDefinition(
        key="death_wave_damage",
        label="Death Wave Damage",
        unit="damage",
        category=MetricCategory.damage,
        kind="observed",
    ),
    "death_ray_damage": MetricDefinition(
        key="death_ray_damage",
        label="Death Ray Damage",
        unit="damage",
        category=MetricCategory.damage,
        kind="observed",
    ),
    "smart_missile_damage": MetricDefinition(
        key="smart_missile_damage",
        label="Smart Missile Damage",
        unit="damage",
        category=MetricCategory.damage,
        kind="observed",
    ),
    "black_hole_damage": MetricDefinition(
        key="black_hole_damage",
        label="Black Hole Damage",
        unit="damage",
        category=MetricCategory.damage,
        kind="observed",
    ),
    "swamp_damage": MetricDefinition(
        key="swamp_damage",
        label="Swamp Damage",
        unit="damage",
        category=MetricCategory.damage,
        kind="observed",
    ),
    "electrons_damage": MetricDefinition(
        key="electrons_damage",
        label="Electrons Damage",
        unit="damage",
        category=MetricCategory.damage,
        kind="observed",
    ),
    "rend_armor_damage": MetricDefinition(
        key="rend_armor_damage",
        label="Rend Armor Damage",
        unit="damage",
        category=MetricCategory.damage,
        kind="observed",
    ),
    "enemies_hit_by_orbs": MetricDefinition(
        key="enemies_hit_by_orbs",
        label="Enemies Hit by Orbs",
        unit="count",
        category=MetricCategory.damage,
        kind="observed",
    ),
    "enemies_destroyed_total": MetricDefinition(
        key="enemies_destroyed_total",
        label="Enemies destroyed (derived total)",
        unit="count",
        category=MetricCategory.enemy_destruction,
        kind="derived",
    ),
    "enemies_destroyed_basic": MetricDefinition(
        key="enemies_destroyed_basic",
        label="Basic",
        unit="count",
        category=MetricCategory.enemy_destruction,
        kind="observed",
    ),
    "enemies_destroyed_fast": MetricDefinition(
        key="enemies_destroyed_fast",
        label="Fast",
        unit="count",
        category=MetricCategory.enemy_destruction,
        kind="observed",
    ),
    "enemies_destroyed_tank": MetricDefinition(
        key="enemies_destroyed_tank",
        label="Tank",
        unit="count",
        category=MetricCategory.enemy_destruction,
        kind="observed",
    ),
    "enemies_destroyed_ranged": MetricDefinition(
        key="enemies_destroyed_ranged",
        label="Ranged",
        unit="count",
        category=MetricCategory.enemy_destruction,
        kind="observed",
    ),
    "enemies_destroyed_boss": MetricDefinition(
        key="enemies_destroyed_boss",
        label="Boss",
        unit="count",
        category=MetricCategory.enemy_destruction,
        kind="observed",
    ),
    "enemies_destroyed_protector": MetricDefinition(
        key="enemies_destroyed_protector",
        label="Protector",
        unit="count",
        category=MetricCategory.enemy_destruction,
        kind="observed",
    ),
    "enemies_destroyed_vampires": MetricDefinition(
        key="enemies_destroyed_vampires",
        label="Vampires",
        unit="count",
        category=MetricCategory.enemy_destruction,
        kind="observed",
    ),
    "enemies_destroyed_rays": MetricDefinition(
        key="enemies_destroyed_rays",
        label="Rays",
        unit="count",
        category=MetricCategory.enemy_destruction,
        kind="observed",
    ),
    "enemies_destroyed_scatters": MetricDefinition(
        key="enemies_destroyed_scatters",
        label="Scatters",
        unit="count",
        category=MetricCategory.enemy_destruction,
        kind="observed",
    ),
    "enemies_destroyed_saboteur": MetricDefinition(
        key="enemies_destroyed_saboteur",
        label="Saboteur",
        unit="count",
        category=MetricCategory.enemy_destruction,
        kind="observed",
    ),
    "enemies_destroyed_commander": MetricDefinition(
        key="enemies_destroyed_commander",
        label="Commander",
        unit="count",
        category=MetricCategory.enemy_destruction,
        kind="observed",
    ),
    "enemies_destroyed_overcharge": MetricDefinition(
        key="enemies_destroyed_overcharge",
        label="Overcharge",
        unit="count",
        category=MetricCategory.enemy_destruction,
        kind="observed",
    ),
    "enemies_destroyed_by_orbs": MetricDefinition(
        key="enemies_destroyed_by_orbs",
        label="Destroyed By Orbs",
        unit="count",
        category=MetricCategory.enemy_destruction,
        kind="observed",
    ),
    "enemies_destroyed_by_thorns": MetricDefinition(
        key="enemies_destroyed_by_thorns",
        label="Destroyed by Thorns",
        unit="count",
        category=MetricCategory.enemy_destruction,
        kind="observed",
    ),
    "enemies_destroyed_by_death_ray": MetricDefinition(
        key="enemies_destroyed_by_death_ray",
        label="Destroyed by Death Ray",
        unit="count",
        category=MetricCategory.enemy_destruction,
        kind="observed",
    ),
    "enemies_destroyed_by_land_mine": MetricDefinition(
        key="enemies_destroyed_by_land_mine",
        label="Destroyed by Land Mine",
        unit="count",
        category=MetricCategory.enemy_destruction,
        kind="observed",
    ),
    "enemies_destroyed_in_spotlight": MetricDefinition(
        key="enemies_destroyed_in_spotlight",
        label="Destroyed in Spotlight",
        unit="count",
        category=MetricCategory.enemy_destruction,
        kind="observed",
    ),
    "enemies_destroyed_in_golden_bot": MetricDefinition(
        key="enemies_destroyed_in_golden_bot",
        label="Destroyed in Golden Bot",
        unit="count",
        category=MetricCategory.enemy_destruction,
        kind="observed",
    ),
    "guardian_summoned_enemies": MetricDefinition(
        key="guardian_summoned_enemies",
        label="Guardian Summoned Enemies",
        unit="count",
        category=MetricCategory.combat,
        kind="observed",
    ),
    "guardian_coins_stolen": MetricDefinition(
        key="guardian_coins_stolen",
        label="Guardian coins stolen",
        unit="coins",
        category=MetricCategory.economy,
        kind="observed",
    ),
    "guardian_coins_fetched": MetricDefinition(
        key="guardian_coins_fetched",
        label="Coins Fetched",
        unit="coins",
        category=MetricCategory.economy,
        kind="observed",
    ),
    "guardian_gems_fetched": MetricDefinition(
        key="guardian_gems_fetched",
        label="Guardian gems fetched",
        unit="count",
        category=MetricCategory.fetch,
        kind="observed",
    ),
    "guardian_medals_fetched": MetricDefinition(
        key="guardian_medals_fetched",
        label="Guardian medals fetched",
        unit="count",
        category=MetricCategory.fetch,
        kind="observed",
    ),
    "guardian_reroll_shards_fetched": MetricDefinition(
        key="guardian_reroll_shards_fetched",
        label="Guardian reroll shards fetched",
        unit="count",
        category=MetricCategory.fetch,
        kind="observed",
    ),
    "guardian_cannon_shards_fetched": MetricDefinition(
        key="guardian_cannon_shards_fetched",
        label="Guardian cannon shards fetched",
        unit="count",
        category=MetricCategory.fetch,
        kind="observed",
    ),
    "guardian_armor_shards_fetched": MetricDefinition(
        key="guardian_armor_shards_fetched",
        label="Guardian armor shards fetched",
        unit="count",
        category=MetricCategory.fetch,
        kind="observed",
    ),
    "guardian_generator_shards_fetched": MetricDefinition(
        key="guardian_generator_shards_fetched",
        label="Guardian generator shards fetched",
        unit="count",
        category=MetricCategory.fetch,
        kind="observed",
    ),
    "guardian_core_shards_fetched": MetricDefinition(
        key="guardian_core_shards_fetched",
        label="Guardian core shards fetched",
        unit="count",
        category=MetricCategory.fetch,
        kind="observed",
    ),
    "guardian_common_modules_fetched": MetricDefinition(
        key="guardian_common_modules_fetched",
        label="Guardian common modules fetched",
        unit="count",
        category=MetricCategory.fetch,
        kind="observed",
    ),
    "guardian_rare_modules_fetched": MetricDefinition(
        key="guardian_rare_modules_fetched",
        label="Guardian rare modules fetched",
        unit="count",
        category=MetricCategory.fetch,
        kind="observed",
    ),
    "uw_uptime_percent": MetricDefinition(
        key="uw_uptime_percent",
        label="Ultimate Weapon uptime",
        unit="percent",
        category=MetricCategory.utility,
        kind="derived",
    ),
    "guardian_activations_per_minute": MetricDefinition(
        key="guardian_activations_per_minute",
        label="Guardian activations/minute",
        unit="activations/min",
        category=MetricCategory.utility,
        kind="derived",
    ),
    "uw_effective_cooldown_seconds": MetricDefinition(
        key="uw_effective_cooldown_seconds",
        label="Ultimate Weapon effective cooldown",
        unit="seconds",
        category=MetricCategory.utility,
        kind="derived",
    ),
    "cooldown_reduction_effective": MetricDefinition(
        key="cooldown_reduction_effective",
        label="Effective cooldown",
        unit="seconds",
        category=MetricCategory.utility,
        kind="derived",
    ),
    "bot_uptime_percent": MetricDefinition(
        key="bot_uptime_percent",
        label="Bot uptime",
        unit="percent",
        category=MetricCategory.utility,
        kind="derived",
    ),
}


def validate_metric_registry() -> None:
    """Validate that MetricDefinition keys and series registry keys match.

    Raises:
        ValueError: When registered metric keys drift between METRICS and the
            DEFAULT_REGISTRY.
    """

    registry_keys = {spec.key for spec in DEFAULT_REGISTRY.list()}
    metric_keys = set(METRICS.keys())
    missing_in_registry = sorted(metric_keys - registry_keys)
    missing_in_metrics = sorted(registry_keys - metric_keys)
    if missing_in_registry or missing_in_metrics:
        raise ValueError(
            "Metric registry mismatch.\n"
            f"- Present in METRICS, missing in DEFAULT_REGISTRY: {missing_in_registry}\n"
            f"- Present in DEFAULT_REGISTRY, missing in METRICS: {missing_in_metrics}\n"
        )


validate_metric_registry()


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
    interest_earned: int | None,
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
        interest_earned: Observed interest earned for the run.
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

    derived_values = _record_derived_values(record)
    derived_interest = derived_values.get("interest_earned")

    if metric_key == "coins_earned":
        return (float(coins) if coins is not None else None, (), ())

    if metric_key == "cash_earned":
        return (float(cash) if cash is not None else None, (), ())

    if metric_key == "interest_earned":
        interest_value = interest_earned if interest_earned is not None else derived_interest
        return (float(interest_value) if interest_value is not None else None, (), ())

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
        raw_text = getattr(record, "raw_text", None)
        if isinstance(raw_text, str) and raw_text.strip():
            return (
                1.0 if is_ultimate_weapon_observed_active(raw_text, ultimate_weapon_name=entity_name) else 0.0,
                (),
                (),
            )
        for rel_name in ("run_combat_uws", "run_utility_uws"):
            related = getattr(record, rel_name, None)
            if related is None:
                continue
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

    if metric_key == "waves_per_hour":
        if wave is None or real_time_seconds is None or real_time_seconds <= 0:
            return None, (), ()
        return (float(wave) * 3600.0 / float(real_time_seconds), (), ("waves/hour = waves_reached / real_time_hours.",))

    if metric_key in RAW_TEXT_METRIC_SPECS and metric_key != "interest_earned":
        persisted = derived_values.get(metric_key)
        if persisted is None:
            return None, (), ("Persisted derived metric missing; reparse or reingest the Battle Report.",)
        return float(persisted), (), ()

    if metric_key == "enemies_destroyed_per_hour":
        if real_time_seconds is None or real_time_seconds <= 0:
            return None, (), ()
        total = _compute_enemies_destroyed_total_from_values(derived_values)
        if total is None:
            return None, (), ()
        return (float(total) * 3600.0 / float(real_time_seconds), (), ("enemies/hour = enemies_destroyed_total / real_time_hours.",))

    if metric_key == "enemies_destroyed_total":
        total = _compute_enemies_destroyed_total_from_values(derived_values)
        if total is None:
            return None, (), ()
        return (float(total), (), ("Derived total: sums per-type destroyed counts; ignores game-reported totals.",))

    if metric_key == "coins_from_other_sources":
        if coins is None:
            return None, (), ()
        other_coins = _compute_other_coins_from_sources(coins=coins, derived_values=derived_values)
        if other_coins is None:
            return None, (), ("Persisted derived metric missing; reparse or reingest the Battle Report.",)
        return other_coins, (), ()

    if metric_key == "cash_from_other_sources":
        if cash is None:
            return None, (), ()
        if not derived_values:
            return None, (), ("Persisted derived metric missing; reparse or reingest the Battle Report.",)
        cash_from_gt = derived_values.get("cash_from_golden_tower") or 0.0
        interest = (interest_earned if interest_earned is not None else derived_interest) or 0.0
        residual = float(cash) - float(cash_from_gt) - float(interest)
        return residual, (), ("Other cash = cash_earned - cash_from_golden_tower - interest_earned.",)

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


def _compute_enemies_destroyed_total_from_values(derived_values: dict[str, float]) -> int | None:
    """Compute enemies destroyed total from persisted derived metrics."""

    metric_keys = (
        "enemies_destroyed_basic",
        "enemies_destroyed_fast",
        "enemies_destroyed_tank",
        "enemies_destroyed_ranged",
        "enemies_destroyed_boss",
        "enemies_destroyed_protector",
        "enemies_destroyed_vampires",
        "enemies_destroyed_rays",
        "enemies_destroyed_scatters",
        "enemies_destroyed_saboteur",
        "enemies_destroyed_commander",
        "enemies_destroyed_overcharge",
    )

    total = 0.0
    has_any = False
    for key in metric_keys:
        observed = derived_values.get(key)
        if observed is None:
            continue
        has_any = True
        total += float(observed)

    if not has_any:
        return None
    try:
        return int(total)
    except (ValueError, OverflowError):
        return None


def _compute_other_coins_from_sources(*, coins: int, derived_values: dict[str, float]) -> float | None:
    """Return residual coins not covered by named sources from persisted values."""

    known_sources = (
        "coins_from_death_wave",
        "coins_from_golden_tower",
        "coins_from_black_hole",
        "coins_from_spotlight",
        "coins_from_orb",
        "coins_from_coin_upgrade",
        "coins_from_coin_bonuses",
        "guardian_coins_stolen",
        "guardian_coins_fetched",
    )

    if not any(key in derived_values for key in known_sources):
        return None

    total_sources = sum(float(derived_values.get(key) or 0.0) for key in known_sources)
    return float(coins) - total_sources


def _record_derived_values(record: object) -> dict[str, float]:
    """Return persisted derived metric values from a record when available."""

    derived = getattr(record, "derived_metrics", None)
    values = getattr(derived, "values", None)
    if isinstance(values, dict):
        return {key: float(value) for key, value in values.items() if value is not None}
    return {}


def category_for_metric(metric_key: str) -> MetricCategory | None:
    """Return the MetricCategory for a metric key, when registered."""

    metric = METRICS.get(metric_key)
    return metric.category if metric is not None else None


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
