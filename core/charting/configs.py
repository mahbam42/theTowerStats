"""Built-in ChartConfig definitions for the Charts dashboard."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Final

from analysis.series_registry import DEFAULT_REGISTRY

from .schema import (
    ChartComparison,
    ChartConfig,
    ChartDerived,
    ChartFilters,
    ChartSeriesConfig,
    ChartUI,
    DateRangeFilterConfig,
    SimpleFilterConfig,
)
from .validator import validate_chart_configs


DEFAULT_START: Final[datetime] = datetime(2025, 12, 9, 0, 0, 0, tzinfo=UTC)


CHART_CONFIGS: Final[tuple[ChartConfig, ...]] = (
    ChartConfig(
        id="coins_earned",
        title="Coins Earned",
        description=None,
        category="top_level",
        chart_type="line",
        metric_series=(ChartSeriesConfig(metric_key="coins_earned"),),
        filters=ChartFilters(
            date_range=DateRangeFilterConfig(enabled=True, default_start=DEFAULT_START),
            tier=SimpleFilterConfig(enabled=True),
            preset=SimpleFilterConfig(enabled=True),
        ),
        ui=ChartUI(show_by_default=True, selectable=True, order=1),
    ),
    ChartConfig(
        id="coins_per_hour",
        title="Coins per Hour",
        description=None,
        category="top_level",
        chart_type="line",
        metric_series=(ChartSeriesConfig(metric_key="coins_earned", transform="rate_per_hour"),),
        filters=ChartFilters(
            date_range=DateRangeFilterConfig(enabled=True, default_start=DEFAULT_START),
            tier=SimpleFilterConfig(enabled=True),
            preset=SimpleFilterConfig(enabled=True),
        ),
        ui=ChartUI(show_by_default=True, selectable=True, order=2),
    ),
    ChartConfig(
        id="coins_by_source",
        title="Coins Earned by Source",
        description="Breakdown of observed coin sources from Battle Reports (aggregated within the current filters).",
        category="top_level",
        chart_type="donut",
        metric_series=(
            ChartSeriesConfig(metric_key="coins_from_death_wave"),
            ChartSeriesConfig(metric_key="coins_from_golden_tower"),
            ChartSeriesConfig(metric_key="coins_from_black_hole"),
            ChartSeriesConfig(metric_key="coins_from_spotlight"),
            ChartSeriesConfig(metric_key="coins_from_orb"),
            ChartSeriesConfig(metric_key="coins_from_coin_upgrade"),
            ChartSeriesConfig(metric_key="coins_from_coin_bonuses"),
            ChartSeriesConfig(metric_key="guardian_coins_stolen"),
            ChartSeriesConfig(metric_key="guardian_coins_fetched"),
        ),
        filters=ChartFilters(
            date_range=DateRangeFilterConfig(enabled=True, default_start=DEFAULT_START),
            tier=SimpleFilterConfig(enabled=True),
            preset=SimpleFilterConfig(enabled=True),
        ),
        ui=ChartUI(show_by_default=False, selectable=True, order=3),
    ),
    ChartConfig(
        id="cash_earned",
        title="Cash Earned",
        description=None,
        category="sub_chart",
        chart_type="line",
        metric_series=(ChartSeriesConfig(metric_key="cash_earned"),),
        filters=ChartFilters(
            date_range=DateRangeFilterConfig(enabled=True, default_start=DEFAULT_START),
            tier=SimpleFilterConfig(enabled=True),
            preset=SimpleFilterConfig(enabled=True),
        ),
        ui=ChartUI(show_by_default=False, selectable=True, order=10),
    ),
    ChartConfig(
        id="cells_earned",
        title="Cells Earned",
        description=None,
        category="sub_chart",
        chart_type="line",
        metric_series=(ChartSeriesConfig(metric_key="cells_earned"),),
        filters=ChartFilters(
            date_range=DateRangeFilterConfig(enabled=True, default_start=DEFAULT_START),
            tier=SimpleFilterConfig(enabled=True),
            preset=SimpleFilterConfig(enabled=True),
        ),
        ui=ChartUI(show_by_default=False, selectable=True, order=11),
    ),
    ChartConfig(
        id="reroll_shards_earned",
        title="Reroll Shards Earned",
        description=None,
        category="sub_chart",
        chart_type="line",
        metric_series=(ChartSeriesConfig(metric_key="reroll_shards_earned"),),
        filters=ChartFilters(
            date_range=DateRangeFilterConfig(enabled=True, default_start=DEFAULT_START),
            tier=SimpleFilterConfig(enabled=True),
            preset=SimpleFilterConfig(enabled=True),
        ),
        ui=ChartUI(show_by_default=False, selectable=True, order=12),
    ),
    ChartConfig(
        id="uw_runs_count",
        title="Runs Using Selected UW",
        description="Count of runs where the selected Ultimate Weapon is present.",
        category="uw_performance",
        chart_type="line",
        metric_series=(ChartSeriesConfig(metric_key="uw_runs_count"),),
        filters=ChartFilters(
            date_range=DateRangeFilterConfig(enabled=True, default_start=DEFAULT_START),
            tier=SimpleFilterConfig(enabled=True),
            preset=SimpleFilterConfig(enabled=True),
            uw=SimpleFilterConfig(enabled=True),
        ),
        ui=ChartUI(show_by_default=False, selectable=True, order=20),
    ),
    ChartConfig(
        id="guardian_runs_count",
        title="Runs Using Selected Guardian Chip",
        description="Count of runs where the selected Guardian Chip is present.",
        category="guardian_stats",
        chart_type="line",
        metric_series=(ChartSeriesConfig(metric_key="guardian_runs_count"),),
        filters=ChartFilters(
            date_range=DateRangeFilterConfig(enabled=True, default_start=DEFAULT_START),
            tier=SimpleFilterConfig(enabled=True),
            preset=SimpleFilterConfig(enabled=True),
            guardian=SimpleFilterConfig(enabled=True),
        ),
        ui=ChartUI(show_by_default=False, selectable=True, order=30),
    ),
    ChartConfig(
        id="guardian_fetch_breakdown",
        title="Guardian Fetch Metrics",
        description="Breakdown of non-coin Guardian fetch outputs (aggregated within the current filters).",
        category="guardian_stats",
        chart_type="donut",
        metric_series=(
            ChartSeriesConfig(metric_key="guardian_gems_fetched"),
            ChartSeriesConfig(metric_key="guardian_medals_fetched"),
            ChartSeriesConfig(metric_key="guardian_reroll_shards_fetched"),
            ChartSeriesConfig(metric_key="guardian_cannon_shards_fetched"),
            ChartSeriesConfig(metric_key="guardian_armor_shards_fetched"),
            ChartSeriesConfig(metric_key="guardian_generator_shards_fetched"),
            ChartSeriesConfig(metric_key="guardian_core_shards_fetched"),
            ChartSeriesConfig(metric_key="guardian_common_modules_fetched"),
            ChartSeriesConfig(metric_key="guardian_rare_modules_fetched"),
        ),
        filters=ChartFilters(
            date_range=DateRangeFilterConfig(enabled=True, default_start=DEFAULT_START),
            tier=SimpleFilterConfig(enabled=True),
            preset=SimpleFilterConfig(enabled=True),
        ),
        ui=ChartUI(show_by_default=False, selectable=True, order=31),
    ),
    ChartConfig(
        id="bot_runs_count",
        title="Runs Using Selected Bot",
        description="Count of runs where the selected Bot is present.",
        category="bot_stats",
        chart_type="line",
        metric_series=(ChartSeriesConfig(metric_key="bot_runs_count"),),
        filters=ChartFilters(
            date_range=DateRangeFilterConfig(enabled=True, default_start=DEFAULT_START),
            tier=SimpleFilterConfig(enabled=True),
            preset=SimpleFilterConfig(enabled=True),
            bot=SimpleFilterConfig(enabled=True),
        ),
        ui=ChartUI(show_by_default=False, selectable=True, order=40),
    ),
    ChartConfig(
        id="coins_earned_by_tier",
        title="Coins Earned (Compare Tiers)",
        description=None,
        category="comparison",
        chart_type="line",
        metric_series=(ChartSeriesConfig(metric_key="coins_earned"),),
        filters=ChartFilters(
            date_range=DateRangeFilterConfig(enabled=True, default_start=DEFAULT_START),
            preset=SimpleFilterConfig(enabled=True),
        ),
        comparison=ChartComparison(mode="by_tier"),
        ui=ChartUI(show_by_default=False, selectable=True, order=50),
    ),
    ChartConfig(
        id="coins_per_hour_by_preset",
        title="Coins per Hour (Compare Presets)",
        description=None,
        category="comparison",
        chart_type="line",
        metric_series=(ChartSeriesConfig(metric_key="coins_earned", transform="rate_per_hour"),),
        filters=ChartFilters(
            date_range=DateRangeFilterConfig(enabled=True, default_start=DEFAULT_START),
            tier=SimpleFilterConfig(enabled=True),
        ),
        comparison=ChartComparison(mode="by_preset"),
        ui=ChartUI(show_by_default=False, selectable=True, order=51),
    ),
    ChartConfig(
        id="coins_per_hour_moving_average",
        title="Coins per Hour (Moving Average)",
        description="Moving average uses the dashboard-level window setting.",
        category="comparison",
        chart_type="line",
        metric_series=(
            ChartSeriesConfig(metric_key="coins_earned", label="Coins per Hour", transform="rate_per_hour"),
            ChartSeriesConfig(metric_key="coins_earned", label="Moving Average", transform="moving_average"),
        ),
        filters=ChartFilters(
            date_range=DateRangeFilterConfig(enabled=True, default_start=DEFAULT_START),
            tier=SimpleFilterConfig(enabled=True),
            preset=SimpleFilterConfig(enabled=True),
        ),
        ui=ChartUI(show_by_default=False, selectable=True, order=52),
    ),
    ChartConfig(
        id="coins_per_wave",
        title="Coins per Wave",
        description="Derived from coins earned divided by waves reached.",
        category="derived",
        chart_type="line",
        metric_series=(
            ChartSeriesConfig(metric_key="coins_earned"),
            ChartSeriesConfig(metric_key="waves_reached"),
        ),
        filters=ChartFilters(
            date_range=DateRangeFilterConfig(enabled=True, default_start=DEFAULT_START),
            tier=SimpleFilterConfig(enabled=True),
            preset=SimpleFilterConfig(enabled=True),
        ),
        derived=ChartDerived(formula="coins_earned / waves_reached", x_axis="time"),
        ui=ChartUI(show_by_default=False, selectable=True, order=60),
    ),
)


_VALIDATION = validate_chart_configs(CHART_CONFIGS, registry=DEFAULT_REGISTRY)
if not _VALIDATION.is_valid:
    joined = "\n".join(_VALIDATION.errors)
    raise ValueError(f"Invalid CHART_CONFIGS:\n{joined}")


CHART_CONFIG_BY_ID: Final[dict[str, ChartConfig]] = {config.id: config for config in CHART_CONFIGS}


def list_selectable_chart_configs() -> tuple[ChartConfig, ...]:
    """Return selectable charts in UI order."""

    selectable = [config for config in CHART_CONFIGS if config.ui.selectable]
    return tuple(sorted(selectable, key=lambda c: (c.ui.order, c.title.lower(), c.id)))


def default_selected_chart_ids() -> tuple[str, ...]:
    """Return default selected chart IDs for the multiselect control."""

    defaults = [config.id for config in CHART_CONFIGS if config.ui.show_by_default and config.ui.selectable]
    return tuple(sorted(defaults))
