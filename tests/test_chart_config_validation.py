"""Tests for ChartConfig validation and dashboard chart introspection."""

from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest

from analysis.series_registry import DEFAULT_REGISTRY
from analysis.series_registry import MetricSeriesRegistry, MetricSeriesSpec
from core.charting.schema import (
    ChartComparison,
    ChartConfig,
    ChartDerived,
    ChartFilters,
    ChartSeriesConfig,
    ChartUI,
    DateRangeFilterConfig,
    SimpleFilterConfig,
)
from core.charting.validator import validate_chart_config


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
                category="utility",
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
                category="utility",
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


@pytest.mark.django_db
def test_dashboard_form_chart_choices_come_from_chart_configs(client) -> None:
    """Populate the charts multiselect from ChartConfig introspection."""

    response = client.get("/")
    assert response.status_code == 200
    chart_form = response.context["chart_form"]
    choices = dict(chart_form.fields["charts"].choices)
    assert "coins_earned" in choices


@pytest.mark.django_db
def test_dashboard_renders_derived_formula_chart(client) -> None:
    """Render a derived chart (coins per wave) from config-driven formulas."""

    from datetime import date as date_type, timezone

    from gamedata.models import BattleReport, BattleReportProgress

    report = BattleReport.objects.create(
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="coinsperwave".ljust(64, "x"),
    )
    BattleReportProgress.objects.create(
        battle_report=report,
        battle_date=datetime(2025, 12, 10, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    response = client.get("/", {"charts": ["coins_per_wave"], "start_date": date_type(2025, 12, 9)})
    assert response.status_code == 200

    panels = {p["id"]: p for p in json.loads(response.context["chart_panels_json"])}
    panel = panels["coins_per_wave"]
    assert panel["labels"] == ["2025-12-10"]
    assert panel["datasets"][0]["data"] == [12.0]
