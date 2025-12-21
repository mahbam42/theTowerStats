"""Tests for ChartConfig validation and dashboard chart introspection."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from analysis.categories import MetricCategory
from analysis.series_registry import DEFAULT_REGISTRY
from analysis.series_registry import MetricSeriesRegistry, MetricSeriesSpec
from core.charting.schema import (
    ChartComparison,
    ChartConfig,
    ChartDerived,
    ChartFilters,
    ChartSeriesConfig,
    ChartUI,
    ComparisonScope,
    DateRangeFilterConfig,
    SimpleFilterConfig,
)
from core.charting.validator import validate_chart_config

pytestmark = pytest.mark.unit


def test_chart_config_validation_rejects_unknown_metric_key() -> None:
    """Reject ChartConfigs that reference missing MetricSeries keys."""

    config = ChartConfig(
        id="bad_chart",
        title="Bad Chart",
        description=None,
        category="top_level",
        chart_type="line",
        metric_series=(ChartSeriesConfig(metric_key="does_not_exist"),),
        filters=ChartFilters(
            date_range=DateRangeFilterConfig(enabled=True, default_start=datetime(2025, 12, 9, tzinfo=UTC)),
            tier=SimpleFilterConfig(enabled=True),
        ),
        ui=ChartUI(show_by_default=False, selectable=True, order=999),
    )
    result = validate_chart_config(config, registry=DEFAULT_REGISTRY)
    assert result.is_valid is False
    assert any("unknown metric_key" in error for error in result.errors)


def test_chart_config_validation_rejects_unknown_formula_identifiers() -> None:
    """Reject derived formulas that reference unknown identifiers."""

    config = ChartConfig(
        id="bad_formula",
        title="Bad Formula",
        description=None,
        category="derived",
        chart_type="line",
        metric_series=(
            ChartSeriesConfig(metric_key="coins_earned"),
            ChartSeriesConfig(metric_key="waves_reached"),
        ),
        filters=ChartFilters(
            date_range=DateRangeFilterConfig(enabled=True, default_start=datetime(2025, 12, 9, tzinfo=UTC)),
        ),
        derived=ChartDerived(formula="coins_earned / not_a_metric", x_axis="time"),
        ui=ChartUI(show_by_default=False, selectable=True, order=999),
    )

    result = validate_chart_config(config, registry=DEFAULT_REGISTRY)
    assert result.is_valid is False
    assert any("unknown identifiers" in error for error in result.errors)


def test_chart_config_validation_requires_comparison_dimension_support() -> None:
    """Require all series to support the comparison dimension (tier/preset/entity)."""

    registry = MetricSeriesRegistry(
        specs=(
            MetricSeriesSpec(
                key="metric",
                label="Metric",
                description=None,
                unit="count",
                category=MetricCategory.utility,
                kind="observed",
                source_model="BattleReport",
                aggregation="sum",
                time_index="timestamp",
                value_field="metric",
                allowed_transforms=frozenset({"none"}),
                supported_filters=frozenset({"date_range"}),
            ),
        )
    )

    config = ChartConfig(
        id="compare_tiers",
        title="Compare Tiers",
        description=None,
        category="comparison",
        chart_type="line",
        metric_series=(ChartSeriesConfig(metric_key="metric"),),
        filters=ChartFilters(
            date_range=DateRangeFilterConfig(enabled=True, default_start=datetime(2025, 12, 9, tzinfo=UTC)),
        ),
        comparison=ChartComparison(mode="by_tier"),
        ui=ChartUI(show_by_default=False, selectable=True, order=999),
    )

    result = validate_chart_config(config, registry=registry)
    assert result.is_valid is False
    assert any("comparison dimension" in error for error in result.errors)


def test_chart_config_validation_by_entity_requires_exactly_one_entity_filter() -> None:
    """Require by-entity comparison to declare exactly one entity filter axis."""

    config = ChartConfig(
        id="compare_entities",
        title="Compare Entities",
        description=None,
        category="comparison",
        chart_type="line",
        metric_series=(ChartSeriesConfig(metric_key="uw_runs_count"),),
        filters=ChartFilters(
            date_range=DateRangeFilterConfig(enabled=True, default_start=datetime(2025, 12, 9, tzinfo=UTC)),
        ),
        comparison=ChartComparison(mode="by_entity", entities=("A", "B")),
        ui=ChartUI(show_by_default=False, selectable=True, order=999),
    )

    result = validate_chart_config(config, registry=DEFAULT_REGISTRY)
    assert result.is_valid is False
    assert any("requires exactly one entity filter enabled" in error for error in result.errors)


def test_chart_config_validation_rejects_derived_axis_mismatch() -> None:
    """Reject derived configs when referenced series axes do not match the x_axis."""

    registry = MetricSeriesRegistry(
        specs=(
            MetricSeriesSpec(
                key="per_wave",
                label="Per wave series",
                description=None,
                unit="count",
                category=MetricCategory.utility,
                kind="observed",
                source_model="BattleReport",
                aggregation="avg",
                time_index="wave_number",
                value_field="value",
                allowed_transforms=frozenset({"none"}),
                supported_filters=frozenset({"date_range"}),
            ),
        )
    )

    config = ChartConfig(
        id="axis_mismatch",
        title="Axis mismatch",
        description=None,
        category="derived",
        chart_type="line",
        metric_series=(ChartSeriesConfig(metric_key="per_wave"),),
        filters=ChartFilters(
            date_range=DateRangeFilterConfig(enabled=True, default_start=datetime(2025, 12, 9, tzinfo=UTC)),
        ),
        derived=ChartDerived(formula="per_wave", x_axis="time"),
        ui=ChartUI(show_by_default=False, selectable=True, order=999),
    )

    result = validate_chart_config(config, registry=registry)
    assert result.is_valid is False
    assert any("incompatible" in error for error in result.errors)


def test_chart_config_validation_rejects_mixed_units_in_multi_series_chart() -> None:
    """Reject multi-series charts that mix incompatible units."""

    config = ChartConfig(
        id="mixed_units",
        title="Mixed units",
        description=None,
        category="top_level",
        chart_type="line",
        metric_series=(
            ChartSeriesConfig(metric_key="coins_earned"),
            ChartSeriesConfig(metric_key="waves_reached"),
        ),
        filters=ChartFilters(
            date_range=DateRangeFilterConfig(enabled=True, default_start=datetime(2025, 12, 9, tzinfo=UTC)),
        ),
        ui=ChartUI(show_by_default=False, selectable=True, order=999),
    )
    result = validate_chart_config(config, registry=DEFAULT_REGISTRY)
    assert result.is_valid is False
    assert any("mixes incompatible units" in error for error in result.errors)


def test_chart_config_validation_rejects_cross_category_metric_mix() -> None:
    """Reject charts that mix MetricCategory values in a single config."""

    config = ChartConfig(
        id="cross_category",
        title="Cross category",
        description=None,
        category="top_level",
        chart_type="line",
        metric_series=(
            ChartSeriesConfig(metric_key="coins_earned"),
            ChartSeriesConfig(metric_key="waves_reached"),
        ),
        filters=ChartFilters(
            date_range=DateRangeFilterConfig(enabled=True, default_start=datetime(2025, 12, 9, tzinfo=UTC)),
        ),
        ui=ChartUI(show_by_default=False, selectable=True, order=999),
    )
    result = validate_chart_config(config, registry=DEFAULT_REGISTRY)
    assert result.is_valid is False
    assert any("mixes metric categories" in error for error in result.errors)


def test_chart_config_validation_requires_donut_to_have_multiple_metrics() -> None:
    """Reject donut charts that declare fewer than two metrics."""

    config = ChartConfig(
        id="donut_one",
        title="Donut one metric",
        description=None,
        category="top_level",
        chart_type="donut",
        metric_series=(ChartSeriesConfig(metric_key="coins_earned"),),
        filters=ChartFilters(
            date_range=DateRangeFilterConfig(enabled=True, default_start=datetime(2025, 12, 9, tzinfo=UTC)),
        ),
        ui=ChartUI(show_by_default=False, selectable=True, order=999),
    )
    result = validate_chart_config(config, registry=DEFAULT_REGISTRY)
    assert result.is_valid is False
    assert any("donut charts must contain at least two" in error for error in result.errors)


def test_chart_config_validation_rejects_derived_on_derived_formulas() -> None:
    """Reject chart-level derived formulas that reference derived metric series."""

    config = ChartConfig(
        id="derived_on_derived",
        title="Derived on derived",
        description=None,
        category="derived",
        chart_type="line",
        metric_series=(
            ChartSeriesConfig(metric_key="coins_per_wave"),
            ChartSeriesConfig(metric_key="coins_earned"),
        ),
        filters=ChartFilters(
            date_range=DateRangeFilterConfig(enabled=True, default_start=datetime(2025, 12, 9, tzinfo=UTC)),
        ),
        derived=ChartDerived(formula="coins_per_wave / coins_earned", x_axis="time"),
        ui=ChartUI(show_by_default=False, selectable=True, order=999),
    )
    result = validate_chart_config(config, registry=DEFAULT_REGISTRY)
    assert result.is_valid is False
    assert any("cannot reference derived metrics" in error for error in result.errors)


def test_chart_config_validation_requires_exactly_two_scopes_for_run_vs_run() -> None:
    """Reject run-vs-run configs missing the two required scopes."""

    config = ChartConfig(
        id="run_vs_run",
        title="Run vs run",
        description=None,
        category="comparison",
        chart_type="line",
        metric_series=(ChartSeriesConfig(metric_key="coins_earned"),),
        filters=ChartFilters(
            date_range=DateRangeFilterConfig(enabled=True, default_start=datetime(2025, 12, 9, tzinfo=UTC)),
        ),
        comparison=ChartComparison(mode="run_vs_run"),
        ui=ChartUI(show_by_default=False, selectable=True, order=999),
    )
    result = validate_chart_config(config, registry=DEFAULT_REGISTRY)
    assert result.is_valid is False
    assert any("require exactly two scopes" in error for error in result.errors)


def test_chart_config_validation_requires_run_ids_for_run_vs_run_scopes() -> None:
    """Reject run-vs-run configs when scope run ids are missing."""

    config = ChartConfig(
        id="run_vs_run_scopes",
        title="Run vs run",
        description=None,
        category="comparison",
        chart_type="line",
        metric_series=(ChartSeriesConfig(metric_key="coins_earned"),),
        filters=ChartFilters(
            date_range=DateRangeFilterConfig(enabled=True, default_start=datetime(2025, 12, 9, tzinfo=UTC)),
        ),
        comparison=ChartComparison(
            mode="run_vs_run",
            scopes=(
                ComparisonScope(label="Run A", run_id=None),
                ComparisonScope(label="Run B", run_id=None),
            ),
        ),
        ui=ChartUI(show_by_default=False, selectable=True, order=999),
    )
    result = validate_chart_config(config, registry=DEFAULT_REGISTRY)
    assert result.is_valid is False
    assert any("requires run_id" in error for error in result.errors)
