"""MetricSeries registry used by declarative chart configs.

This registry is a thin, analysis-layer description of which metric keys exist,
which filter dimensions they support, and which transforms are allowed. It is
used by the ChartConfig validator and the dashboard renderer.

The registry remains Django-free and describes *capabilities* only. Query
scoping (date range, tier, preset, entity selection) happens at the view layer
before records are passed into the Analysis Engine.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import Final, Iterable, Literal

from .categories import MetricCategory

MetricTransform = Literal["none", "moving_average", "cumulative", "rate_per_hour"]

FilterKey = Literal["date_range", "tier", "preset", "uw", "guardian", "bot"]
Aggregation = Literal["sum", "avg"]
SourceModel = Literal["BattleReport", "RunCombat", "RunGuardian", "RunBots"]
TimeIndex = Literal["timestamp", "wave_number"]


@dataclass(frozen=True, slots=True)
class FormulaInspection:
    """Result of inspecting a derived-metric formula.

    Args:
        referenced_metric_keys: Metric keys referenced by name in the formula.
        unknown_identifiers: Identifiers present in the formula that are not registered metric keys.
        is_valid_syntax: Whether the formula parses as a Python expression.
        is_safe: Whether the formula uses only the supported safe expression subset.
    """

    referenced_metric_keys: frozenset[str]
    unknown_identifiers: frozenset[str]
    is_valid_syntax: bool
    is_safe: bool


@dataclass(frozen=True, slots=True)
class MetricSeriesSpec:
    """Describe a chartable metric series.

    Args:
        key: Stable metric key referenced by ChartConfig.metric_series.metric_key.
        label: Human-friendly label.
        description: Optional description for Chart Builder / UI tooltips.
        unit: Display unit string.
        category: Semantic category used for registry validation.
        kind: Either "observed" or "derived".
        source_model: Source model family backing the series.
        aggregation: Default aggregation used by dashboard charts.
        time_index: The x-axis index used when charting the series.
        value_field: Field name or computed accessor label.
        allowed_transforms: Allowed transforms for this metric.
        supported_filters: Filter dimensions supported by this metric.
    """

    key: str
    label: str
    description: str | None
    unit: str
    category: MetricCategory
    kind: str
    source_model: SourceModel
    aggregation: Aggregation
    time_index: TimeIndex
    value_field: str
    allowed_transforms: frozenset[MetricTransform]
    supported_filters: frozenset[FilterKey]


class MetricSeriesRegistry:
    """Lookup and validation helpers for metric series definitions."""

    def __init__(self, specs: Iterable[MetricSeriesSpec]) -> None:
        """Initialize a registry from a collection of specs."""

        self._specs: dict[str, MetricSeriesSpec] = {}
        for spec in specs:
            if spec.key in self._specs:
                raise ValueError(f"Duplicate MetricSeriesSpec key: {spec.key!r}")
            if not isinstance(spec.category, MetricCategory):
                raise ValueError(
                    f"MetricSeriesSpec[{spec.key!r}] has invalid category={spec.category!r}; expected MetricCategory."
                )
            self._specs[spec.key] = spec

    def get(self, key: str) -> MetricSeriesSpec | None:
        """Return a spec for a metric key, or None when missing."""

        return self._specs.get(key)

    def list(self) -> tuple[MetricSeriesSpec, ...]:
        """Return all specs in a stable order."""

        return tuple(self._specs[key] for key in sorted(self._specs.keys()))

    def formula_metric_keys(self, formula: str) -> set[str]:
        """Return metric keys referenced by a derived formula.

        Prefer `inspect_formula` when validation needs unknown identifier
        detection and safety guarantees.
        """

        return set(self.inspect_formula(formula).referenced_metric_keys)

    def inspect_formula(self, formula: str) -> FormulaInspection:
        """Inspect a derived-metric formula for identifiers and safety.

        The formula language matches `analysis.derived_formula.evaluate_formula`:
        constants, metric-key identifiers, unary +/- and binary + - * / only.

        Args:
            formula: An expression containing metric keys as variable names.

        Returns:
            FormulaInspection describing referenced/unknown identifiers and whether
            the expression is syntactically valid and safe.
        """

        try:
            tree = ast.parse(formula, mode="eval")
        except SyntaxError:
            return FormulaInspection(
                referenced_metric_keys=frozenset(),
                unknown_identifiers=frozenset(),
                is_valid_syntax=False,
                is_safe=False,
            )

        names: set[str] = set()
        is_safe = True
        for node in ast.walk(tree):
            if isinstance(node, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.UAdd, ast.USub)):
                continue

            if isinstance(node, ast.Name):
                names.add(node.id)
                continue

            if isinstance(node, ast.Constant):
                if isinstance(node.value, (int, float)):
                    continue
                is_safe = False
                continue

            if isinstance(node, ast.UnaryOp):
                if isinstance(node.op, (ast.UAdd, ast.USub)):
                    continue
                is_safe = False
                continue

            if isinstance(node, ast.BinOp):
                if isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
                    continue
                is_safe = False
                continue

            if isinstance(node, (ast.Expression, ast.Load)):
                continue

            is_safe = False

        referenced = {name for name in names if name in self._specs}
        unknown = {name for name in names if name not in self._specs}
        return FormulaInspection(
            referenced_metric_keys=frozenset(referenced),
            unknown_identifiers=frozenset(unknown),
            is_valid_syntax=True,
            is_safe=is_safe,
        )


_COMMON_FILTERS: Final[frozenset[FilterKey]] = frozenset({"date_range", "tier", "preset"})


DEFAULT_REGISTRY: Final[MetricSeriesRegistry] = MetricSeriesRegistry(
    specs=(
        MetricSeriesSpec(
            key="coins_earned",
            label="Coins earned",
            description=None,
            unit="coins",
            category=MetricCategory.economy,
            kind="observed",
            source_model="BattleReport",
            aggregation="sum",
            time_index="timestamp",
            value_field="coins_earned",
            allowed_transforms=frozenset({"none", "rate_per_hour", "cumulative", "moving_average"}),
            supported_filters=_COMMON_FILTERS,
        ),
        MetricSeriesSpec(
            key="cash_earned",
            label="Cash earned",
            description=None,
            unit="cash",
            category=MetricCategory.economy,
            kind="observed",
            source_model="BattleReport",
            aggregation="sum",
            time_index="timestamp",
            value_field="cash_earned",
            allowed_transforms=frozenset({"none", "cumulative", "moving_average"}),
            supported_filters=_COMMON_FILTERS,
        ),
        MetricSeriesSpec(
            key="cells_earned",
            label="Cells earned",
            description=None,
            unit="cells",
            category=MetricCategory.economy,
            kind="observed",
            source_model="BattleReport",
            aggregation="sum",
            time_index="timestamp",
            value_field="cells_earned",
            allowed_transforms=frozenset({"none", "cumulative", "moving_average"}),
            supported_filters=_COMMON_FILTERS,
        ),
        MetricSeriesSpec(
            key="reroll_shards_earned",
            label="Reroll shards earned",
            description=None,
            unit="shards",
            category=MetricCategory.economy,
            kind="observed",
            source_model="BattleReport",
            aggregation="sum",
            time_index="timestamp",
            value_field="reroll_shards_earned",
            allowed_transforms=frozenset({"none", "cumulative", "moving_average"}),
            supported_filters=_COMMON_FILTERS,
        ),
        MetricSeriesSpec(
            key="reroll_dice_earned",
            label="Reroll dice earned",
            description="Alias for reroll shards earned (legacy naming).",
            unit="shards",
            category=MetricCategory.economy,
            kind="observed",
            source_model="BattleReport",
            aggregation="sum",
            time_index="timestamp",
            value_field="reroll_shards_earned",
            allowed_transforms=frozenset({"none", "cumulative", "moving_average"}),
            supported_filters=_COMMON_FILTERS,
        ),
        MetricSeriesSpec(
            key="waves_reached",
            label="Waves reached",
            description=None,
            unit="waves",
            category=MetricCategory.utility,
            kind="observed",
            source_model="BattleReport",
            aggregation="avg",
            time_index="timestamp",
            value_field="wave",
            allowed_transforms=frozenset({"none", "cumulative", "moving_average"}),
            supported_filters=_COMMON_FILTERS,
        ),
        MetricSeriesSpec(
            key="coins_per_wave",
            label="Coins per wave",
            description="Computed as coins earned divided by waves reached.",
            unit="coins/wave",
            category=MetricCategory.economy,
            kind="derived",
            source_model="BattleReport",
            aggregation="avg",
            time_index="timestamp",
            value_field="coins_earned / wave",
            allowed_transforms=frozenset({"none", "moving_average"}),
            supported_filters=_COMMON_FILTERS,
        ),
        MetricSeriesSpec(
            key="coins_per_hour",
            label="Coins/hour",
            description="Observed coins earned divided by real time (hours).",
            unit="coins/hour",
            category=MetricCategory.economy,
            kind="observed",
            source_model="BattleReport",
            aggregation="avg",
            time_index="timestamp",
            value_field="coins_per_hour",
            allowed_transforms=frozenset({"none", "moving_average"}),
            supported_filters=_COMMON_FILTERS,
        ),
        MetricSeriesSpec(
            key="uw_runs_count",
            label="Runs using selected ultimate weapon",
            description=None,
            unit="runs",
            category=MetricCategory.utility,
            kind="observed",
            source_model="RunCombat",
            aggregation="sum",
            time_index="timestamp",
            value_field="ultimate_weapon_present",
            allowed_transforms=frozenset({"none", "cumulative", "moving_average"}),
            supported_filters=frozenset({"date_range", "tier", "preset", "uw"}),
        ),
        MetricSeriesSpec(
            key="guardian_runs_count",
            label="Runs using selected guardian chip",
            description=None,
            unit="runs",
            category=MetricCategory.utility,
            kind="observed",
            source_model="RunGuardian",
            aggregation="sum",
            time_index="timestamp",
            value_field="guardian_chip_present",
            allowed_transforms=frozenset({"none", "cumulative", "moving_average"}),
            supported_filters=frozenset({"date_range", "tier", "preset", "guardian"}),
        ),
        MetricSeriesSpec(
            key="bot_runs_count",
            label="Runs using selected bot",
            description=None,
            unit="runs",
            category=MetricCategory.utility,
            kind="observed",
            source_model="RunBots",
            aggregation="sum",
            time_index="timestamp",
            value_field="bot_present",
            allowed_transforms=frozenset({"none", "cumulative", "moving_average"}),
            supported_filters=frozenset({"date_range", "tier", "preset", "bot"}),
        ),
        MetricSeriesSpec(
            key="uw_uptime_percent",
            label="Ultimate Weapon uptime",
            description="Derived uptime percent for the selected Ultimate Weapon.",
            unit="percent",
            category=MetricCategory.utility,
            kind="derived",
            source_model="RunCombat",
            aggregation="avg",
            time_index="timestamp",
            value_field="uw_uptime_percent",
            allowed_transforms=frozenset({"none", "moving_average"}),
            supported_filters=frozenset({"date_range", "tier", "preset", "uw"}),
        ),
        MetricSeriesSpec(
            key="guardian_activations_per_minute",
            label="Guardian activations/minute",
            description="Derived activations/minute for the selected Guardian Chip.",
            unit="activations/min",
            category=MetricCategory.utility,
            kind="derived",
            source_model="RunGuardian",
            aggregation="avg",
            time_index="timestamp",
            value_field="guardian_activations_per_minute",
            allowed_transforms=frozenset({"none", "moving_average"}),
            supported_filters=frozenset({"date_range", "tier", "preset", "guardian"}),
        ),
        MetricSeriesSpec(
            key="uw_effective_cooldown_seconds",
            label="Ultimate Weapon effective cooldown",
            description="Derived cooldown seconds for the selected Ultimate Weapon.",
            unit="seconds",
            category=MetricCategory.utility,
            kind="derived",
            source_model="RunCombat",
            aggregation="avg",
            time_index="timestamp",
            value_field="uw_effective_cooldown_seconds",
            allowed_transforms=frozenset({"none", "moving_average"}),
            supported_filters=frozenset({"date_range", "tier", "preset", "uw"}),
        ),
        MetricSeriesSpec(
            key="bot_uptime_percent",
            label="Bot uptime",
            description="Derived uptime percent for the selected Bot.",
            unit="percent",
            category=MetricCategory.utility,
            kind="derived",
            source_model="RunBots",
            aggregation="avg",
            time_index="timestamp",
            value_field="bot_uptime_percent",
            allowed_transforms=frozenset({"none", "moving_average"}),
            supported_filters=frozenset({"date_range", "tier", "preset", "bot"}),
        ),
        MetricSeriesSpec(
            key="cooldown_reduction_effective",
            label="Effective cooldown",
            description="Entity-scoped effective cooldown in seconds (placeholder for future reduction modeling).",
            unit="seconds",
            category=MetricCategory.utility,
            kind="derived",
            source_model="RunCombat",
            aggregation="avg",
            time_index="timestamp",
            value_field="effective_cooldown_seconds",
            allowed_transforms=frozenset({"none", "moving_average"}),
            supported_filters=frozenset({"date_range", "tier", "preset", "uw", "guardian", "bot"}),
        ),
        MetricSeriesSpec(
            key="coins_from_death_wave",
            label="Coins From Death Wave",
            description="Battle Report utility breakdown: coins earned from Death Wave.",
            unit="coins",
            category=MetricCategory.economy,
            kind="observed",
            source_model="BattleReport",
            aggregation="sum",
            time_index="timestamp",
            value_field="coins_from_death_wave",
            allowed_transforms=frozenset({"none", "cumulative", "moving_average"}),
            supported_filters=_COMMON_FILTERS,
        ),
        MetricSeriesSpec(
            key="coins_from_golden_tower",
            label="Coins From Golden Tower",
            description="Battle Report utility breakdown: coins earned from Golden Tower.",
            unit="coins",
            category=MetricCategory.economy,
            kind="observed",
            source_model="BattleReport",
            aggregation="sum",
            time_index="timestamp",
            value_field="coins_from_golden_tower",
            allowed_transforms=frozenset({"none", "cumulative", "moving_average"}),
            supported_filters=_COMMON_FILTERS,
        ),
        MetricSeriesSpec(
            key="cash_from_golden_tower",
            label="Cash From Golden Tower",
            description="Battle Report utility breakdown: cash earned from Golden Tower.",
            unit="cash",
            category=MetricCategory.economy,
            kind="observed",
            source_model="BattleReport",
            aggregation="sum",
            time_index="timestamp",
            value_field="cash_from_golden_tower",
            allowed_transforms=frozenset({"none", "cumulative", "moving_average"}),
            supported_filters=_COMMON_FILTERS,
        ),
        MetricSeriesSpec(
            key="coins_from_black_hole",
            label="Coins From Black Hole",
            description="Battle Report utility breakdown: coins earned from Black Hole.",
            unit="coins",
            category=MetricCategory.economy,
            kind="observed",
            source_model="BattleReport",
            aggregation="sum",
            time_index="timestamp",
            value_field="coins_from_black_hole",
            allowed_transforms=frozenset({"none", "cumulative", "moving_average"}),
            supported_filters=_COMMON_FILTERS,
        ),
        MetricSeriesSpec(
            key="coins_from_spotlight",
            label="Coins From Spotlight",
            description="Battle Report utility breakdown: coins earned from Spotlight.",
            unit="coins",
            category=MetricCategory.economy,
            kind="observed",
            source_model="BattleReport",
            aggregation="sum",
            time_index="timestamp",
            value_field="coins_from_spotlight",
            allowed_transforms=frozenset({"none", "cumulative", "moving_average"}),
            supported_filters=_COMMON_FILTERS,
        ),
        MetricSeriesSpec(
            key="coins_from_orb",
            label="Coins From Orb",
            description="Battle Report utility breakdown: coins earned from Orbs.",
            unit="coins",
            category=MetricCategory.economy,
            kind="observed",
            source_model="BattleReport",
            aggregation="sum",
            time_index="timestamp",
            value_field="coins_from_orb",
            allowed_transforms=frozenset({"none", "cumulative", "moving_average"}),
            supported_filters=_COMMON_FILTERS,
        ),
        MetricSeriesSpec(
            key="coins_from_coin_upgrade",
            label="Coins from Coin Upgrade",
            description="Battle Report utility breakdown: coins earned from coin upgrades.",
            unit="coins",
            category=MetricCategory.economy,
            kind="observed",
            source_model="BattleReport",
            aggregation="sum",
            time_index="timestamp",
            value_field="coins_from_coin_upgrade",
            allowed_transforms=frozenset({"none", "cumulative", "moving_average"}),
            supported_filters=_COMMON_FILTERS,
        ),
        MetricSeriesSpec(
            key="coins_from_coin_bonuses",
            label="Coins from Coin Bonuses",
            description="Battle Report utility breakdown: coins earned from coin bonuses.",
            unit="coins",
            category=MetricCategory.economy,
            kind="observed",
            source_model="BattleReport",
            aggregation="sum",
            time_index="timestamp",
            value_field="coins_from_coin_bonuses",
            allowed_transforms=frozenset({"none", "cumulative", "moving_average"}),
            supported_filters=_COMMON_FILTERS,
        ),
        MetricSeriesSpec(
            key="coins_from_other_sources",
            label="Other coins",
            description="Residual coins not covered by named sources; ensures sources sum to total coins earned.",
            unit="coins",
            category=MetricCategory.economy,
            kind="observed",
            source_model="BattleReport",
            aggregation="sum",
            time_index="timestamp",
            value_field="coins_from_other_sources",
            allowed_transforms=frozenset({"none", "cumulative", "moving_average"}),
            supported_filters=_COMMON_FILTERS,
        ),
        MetricSeriesSpec(
            key="guardian_damage",
            label="Guardian Damage",
            description="Battle Report Guardian section: damage dealt by the Guardian.",
            unit="damage",
            category=MetricCategory.combat,
            kind="observed",
            source_model="BattleReport",
            aggregation="avg",
            time_index="timestamp",
            value_field="guardian_damage",
            allowed_transforms=frozenset({"none", "moving_average"}),
            supported_filters=_COMMON_FILTERS,
        ),
        MetricSeriesSpec(
            key="guardian_summoned_enemies",
            label="Guardian Summoned Enemies",
            description="Battle Report Guardian section: summoned enemies count.",
            unit="count",
            category=MetricCategory.combat,
            kind="observed",
            source_model="BattleReport",
            aggregation="avg",
            time_index="timestamp",
            value_field="guardian_summoned_enemies",
            allowed_transforms=frozenset({"none", "moving_average"}),
            supported_filters=_COMMON_FILTERS,
        ),
        MetricSeriesSpec(
            key="guardian_coins_stolen",
            label="Guardian coins stolen",
            description="Battle Report Guardian section: coins stolen (rolls up into Coins Earned by Source).",
            unit="coins",
            category=MetricCategory.economy,
            kind="observed",
            source_model="BattleReport",
            aggregation="sum",
            time_index="timestamp",
            value_field="guardian_coins_stolen",
            allowed_transforms=frozenset({"none", "cumulative", "moving_average"}),
            supported_filters=_COMMON_FILTERS,
        ),
        MetricSeriesSpec(
            key="guardian_coins_fetched",
            label="Coins Fetched",
            description="Battle Report Guardian section: coins fetched (rolls up into Coins Earned by Source).",
            unit="coins",
            category=MetricCategory.economy,
            kind="observed",
            source_model="BattleReport",
            aggregation="sum",
            time_index="timestamp",
            value_field="guardian_coins_fetched",
            allowed_transforms=frozenset({"none", "cumulative", "moving_average"}),
            supported_filters=_COMMON_FILTERS,
        ),
        MetricSeriesSpec(
            key="guardian_gems_fetched",
            label="Gems",
            description="Battle Report Guardian section: gems fetched.",
            unit="count",
            category=MetricCategory.fetch,
            kind="observed",
            source_model="BattleReport",
            aggregation="sum",
            time_index="timestamp",
            value_field="guardian_gems_fetched",
            allowed_transforms=frozenset({"none", "cumulative", "moving_average"}),
            supported_filters=_COMMON_FILTERS,
        ),
        MetricSeriesSpec(
            key="guardian_medals_fetched",
            label="Medals",
            description="Battle Report Guardian section: medals fetched.",
            unit="count",
            category=MetricCategory.fetch,
            kind="observed",
            source_model="BattleReport",
            aggregation="sum",
            time_index="timestamp",
            value_field="guardian_medals_fetched",
            allowed_transforms=frozenset({"none", "cumulative", "moving_average"}),
            supported_filters=_COMMON_FILTERS,
        ),
        MetricSeriesSpec(
            key="guardian_reroll_shards_fetched",
            label="Reroll Shards",
            description="Battle Report Guardian section: reroll shards fetched.",
            unit="count",
            category=MetricCategory.fetch,
            kind="observed",
            source_model="BattleReport",
            aggregation="sum",
            time_index="timestamp",
            value_field="guardian_reroll_shards_fetched",
            allowed_transforms=frozenset({"none", "cumulative", "moving_average"}),
            supported_filters=_COMMON_FILTERS,
        ),
        MetricSeriesSpec(
            key="guardian_cannon_shards_fetched",
            label="Cannon Shards",
            description="Battle Report Guardian section: cannon shards fetched.",
            unit="count",
            category=MetricCategory.fetch,
            kind="observed",
            source_model="BattleReport",
            aggregation="sum",
            time_index="timestamp",
            value_field="guardian_cannon_shards_fetched",
            allowed_transforms=frozenset({"none", "cumulative", "moving_average"}),
            supported_filters=_COMMON_FILTERS,
        ),
        MetricSeriesSpec(
            key="guardian_armor_shards_fetched",
            label="Armor Shards",
            description="Battle Report Guardian section: armor shards fetched.",
            unit="count",
            category=MetricCategory.fetch,
            kind="observed",
            source_model="BattleReport",
            aggregation="sum",
            time_index="timestamp",
            value_field="guardian_armor_shards_fetched",
            allowed_transforms=frozenset({"none", "cumulative", "moving_average"}),
            supported_filters=_COMMON_FILTERS,
        ),
        MetricSeriesSpec(
            key="guardian_generator_shards_fetched",
            label="Generator Shards",
            description="Battle Report Guardian section: generator shards fetched.",
            unit="count",
            category=MetricCategory.fetch,
            kind="observed",
            source_model="BattleReport",
            aggregation="sum",
            time_index="timestamp",
            value_field="guardian_generator_shards_fetched",
            allowed_transforms=frozenset({"none", "cumulative", "moving_average"}),
            supported_filters=_COMMON_FILTERS,
        ),
        MetricSeriesSpec(
            key="guardian_core_shards_fetched",
            label="Core Shards",
            description="Battle Report Guardian section: core shards fetched.",
            unit="count",
            category=MetricCategory.fetch,
            kind="observed",
            source_model="BattleReport",
            aggregation="sum",
            time_index="timestamp",
            value_field="guardian_core_shards_fetched",
            allowed_transforms=frozenset({"none", "cumulative", "moving_average"}),
            supported_filters=_COMMON_FILTERS,
        ),
        MetricSeriesSpec(
            key="guardian_common_modules_fetched",
            label="Common Modules",
            description="Battle Report Guardian section: common modules fetched.",
            unit="count",
            category=MetricCategory.fetch,
            kind="observed",
            source_model="BattleReport",
            aggregation="sum",
            time_index="timestamp",
            value_field="guardian_common_modules_fetched",
            allowed_transforms=frozenset({"none", "cumulative", "moving_average"}),
            supported_filters=_COMMON_FILTERS,
        ),
        MetricSeriesSpec(
            key="guardian_rare_modules_fetched",
            label="Rare Modules",
            description="Battle Report Guardian section: rare modules fetched.",
            unit="count",
            category=MetricCategory.fetch,
            kind="observed",
            source_model="BattleReport",
            aggregation="sum",
            time_index="timestamp",
            value_field="guardian_rare_modules_fetched",
            allowed_transforms=frozenset({"none", "cumulative", "moving_average"}),
            supported_filters=_COMMON_FILTERS,
        ),
    )
)
