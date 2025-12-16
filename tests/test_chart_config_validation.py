"""Tests for ChartConfig validation and dashboard chart introspection."""

from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest

from analysis.series_registry import DEFAULT_REGISTRY
from core.charting.schema import (
    ChartConfig,
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

