"""Registry definitions for Explore metric and breakdown metadata."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal

from .metrics import METRICS
from .quantity import UnitType
from .series_registry import DEFAULT_REGISTRY

Aggregation = Literal["sum", "count", "avg"]
BreakdownKind = Literal["field", "metric_group"]


@dataclass(frozen=True, slots=True)
class ExploreMetricDefinition:
    """Metadata for Explore metrics.

    Attributes:
        key: Stable metric key.
        label: Human-friendly label.
        unit: Display unit string for formatting.
        unit_type: Unit category for validation.
        allowed_aggregations: Supported aggregations for this metric.
        is_counter: Whether the metric represents a count-like value.
        is_breakdown_eligible: Whether the metric can be grouped by breakdowns.
        source_fields: Source fields used for computation or lookup.
        derived_logic: Optional description of derived logic.
        deprecated_in_version: Optional deprecation marker.
    """

    key: str
    label: str
    unit: str
    unit_type: UnitType
    allowed_aggregations: tuple[Aggregation, ...]
    is_counter: bool
    is_breakdown_eligible: bool
    source_fields: tuple[str, ...]
    derived_logic: str | None
    deprecated_in_version: str | None


@dataclass(frozen=True, slots=True)
class ExploreBreakdownDefinition:
    """Definition for a semantic Explore breakdown."""

    key: str
    label: str
    kind: BreakdownKind
    field: str | None = None
    metric_keys: tuple[str, ...] | None = None
    compatible_metric_keys: tuple[str, ...] | None = None


def _unit_type_for_unit(unit: str) -> UnitType:
    """Map a metric unit string to a UnitType."""

    normalized = (unit or "").strip().casefold()
    if normalized.startswith("coins"):
        return UnitType.coins
    if normalized.startswith("cash"):
        return UnitType.cash
    if "damage" in normalized:
        return UnitType.damage
    if normalized in {"hours", "hour", "seconds", "second", "s"}:
        return UnitType.time
    if normalized in {"percent", "%", "multiplier", "x", "activations/min"}:
        return UnitType.multiplier
    return UnitType.count


def _allowed_aggregations_for_unit(*, aggregation: str) -> tuple[Aggregation, ...]:
    """Return supported aggregations based on the chart registry default."""

    if aggregation == "sum":
        return ("sum", "count", "avg")
    if aggregation == "avg":
        return ("avg", "count")
    return ("count",)


def build_explore_metric_registry() -> dict[str, ExploreMetricDefinition]:
    """Build the Explore metric registry from the Chart Builder registry."""

    registry: dict[str, ExploreMetricDefinition] = {}
    for spec in DEFAULT_REGISTRY.list():
        metric = METRICS.get(spec.key)
        unit = metric.unit if metric is not None else spec.unit
        unit_type = _unit_type_for_unit(unit)
        allowed_aggregations = _allowed_aggregations_for_unit(aggregation=spec.aggregation)
        is_counter = unit_type == UnitType.count
        registry[spec.key] = ExploreMetricDefinition(
            key=spec.key,
            label=spec.label,
            unit=unit,
            unit_type=unit_type,
            allowed_aggregations=allowed_aggregations,
            is_counter=is_counter,
            is_breakdown_eligible=True,
            source_fields=(spec.value_field,),
            derived_logic=None if spec.kind == "observed" else spec.value_field,
            deprecated_in_version=None,
        )
    return registry


def list_explore_metrics(registry: dict[str, ExploreMetricDefinition]) -> tuple[ExploreMetricDefinition, ...]:
    """Return Explore metrics in a stable order."""

    return tuple(registry[key] for key in sorted(registry.keys()))


DAMAGE_SOURCE_METRICS: Final[tuple[str, ...]] = (
    "projectiles_damage",
    "thorn_damage",
    "orb_damage",
    "land_mine_damage",
    "inner_land_mine_damage",
    "chain_lightning_damage",
    "death_wave_damage",
    "death_ray_damage",
    "smart_missile_damage",
    "black_hole_damage",
    "swamp_damage",
    "electrons_damage",
    "rend_armor_damage",
)

ENEMY_TYPE_METRICS: Final[tuple[str, ...]] = (
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

COIN_SOURCE_METRICS: Final[tuple[str, ...]] = (
    "coins_from_death_wave",
    "coins_from_golden_tower",
    "coins_from_black_hole",
    "coins_from_spotlight",
    "coins_from_orb",
    "coins_from_coin_upgrade",
    "coins_from_coin_bonuses",
    "guardian_coins_stolen",
    "guardian_coins_fetched",
    "coins_from_other_sources",
)

GUARDIAN_OUTCOME_METRICS: Final[tuple[str, ...]] = (
    "guardian_gems_fetched",
    "guardian_medals_fetched",
    "guardian_reroll_shards_fetched",
    "guardian_cannon_shards_fetched",
    "guardian_armor_shards_fetched",
    "guardian_generator_shards_fetched",
    "guardian_core_shards_fetched",
    "guardian_common_modules_fetched",
    "guardian_rare_modules_fetched",
)


DEFAULT_BREAKDOWNS: Final[dict[str, ExploreBreakdownDefinition]] = {
    "damage_source": ExploreBreakdownDefinition(
        key="damage_source",
        label="Damage Source",
        kind="metric_group",
        metric_keys=DAMAGE_SOURCE_METRICS,
        compatible_metric_keys=("damage_dealt", *DAMAGE_SOURCE_METRICS),
    ),
    "enemy_type": ExploreBreakdownDefinition(
        key="enemy_type",
        label="Enemy Type",
        kind="metric_group",
        metric_keys=ENEMY_TYPE_METRICS,
        compatible_metric_keys=("enemies_destroyed_total", *ENEMY_TYPE_METRICS),
    ),
    "coin_source": ExploreBreakdownDefinition(
        key="coin_source",
        label="Coin Source",
        kind="metric_group",
        metric_keys=COIN_SOURCE_METRICS,
        compatible_metric_keys=("coins_earned", *COIN_SOURCE_METRICS),
    ),
    "guardian_outcome": ExploreBreakdownDefinition(
        key="guardian_outcome",
        label="Guardian Outcome",
        kind="metric_group",
        metric_keys=GUARDIAN_OUTCOME_METRICS,
        compatible_metric_keys=GUARDIAN_OUTCOME_METRICS,
    ),
    "run": ExploreBreakdownDefinition(
        key="run",
        label="Run",
        kind="field",
        field="run",
    ),
    "tier": ExploreBreakdownDefinition(
        key="tier",
        label="Tier",
        kind="field",
        field="tier",
    ),
    "preset": ExploreBreakdownDefinition(
        key="preset",
        label="Preset",
        kind="field",
        field="preset",
    ),
    "tournament_rank": ExploreBreakdownDefinition(
        key="tournament_rank",
        label="Tournament Rank",
        kind="field",
        field="tournament_rank",
    ),
    "date": ExploreBreakdownDefinition(
        key="date",
        label="Date (daily)",
        kind="field",
        field="date",
    ),
    "death_cause": ExploreBreakdownDefinition(
        key="death_cause",
        label="Death cause",
        kind="field",
        field="death_cause",
    ),
}


def list_explore_breakdowns() -> tuple[ExploreBreakdownDefinition, ...]:
    """Return Explore breakdowns in a stable order."""

    return tuple(DEFAULT_BREAKDOWNS[key] for key in sorted(DEFAULT_BREAKDOWNS.keys()))


def metric_units_for_breakdown(
    breakdown: ExploreBreakdownDefinition,
    registry: dict[str, ExploreMetricDefinition],
) -> set[str]:
    """Return the unit labels for a metric-group breakdown."""

    if breakdown.kind != "metric_group" or not breakdown.metric_keys:
        return set()
    units: set[str] = set()
    for key in breakdown.metric_keys:
        metric = registry.get(key)
        if metric is None:
            continue
        units.add(metric.unit)
    return units
