"""Unit tests for 100% stacked bar chart normalization."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from analysis.categories import MetricCategory
from analysis.dto import MetricPoint
from analysis.series_registry import MetricSeriesRegistry, MetricSeriesSpec
from core.charting.render import render_chart
from core.charting.schema import ChartConfig, ChartFilters, ChartSeriesConfig, ChartUI, DateRangeFilterConfig

pytestmark = pytest.mark.unit


def test_stacked_percent_bar_sums_to_100(monkeypatch: pytest.MonkeyPatch) -> None:
    """Each x-axis label should sum to ~100% across stacked datasets."""

    registry = MetricSeriesRegistry(
        specs=(
            MetricSeriesSpec(
                key="damage_a",
                label="Damage A",
                description=None,
                unit="damage",
                category=MetricCategory.damage,
                kind="observed",
                source_model="BattleReport",
                aggregation="sum",
                time_index="timestamp",
                value_field="value",
                allowed_transforms=frozenset({"none"}),
                supported_filters=frozenset({"date_range"}),
            ),
            MetricSeriesSpec(
                key="damage_b",
                label="Damage B",
                description=None,
                unit="damage",
                category=MetricCategory.damage,
                kind="observed",
                source_model="BattleReport",
                aggregation="sum",
                time_index="timestamp",
                value_field="value",
                allowed_transforms=frozenset({"none"}),
                supported_filters=frozenset({"date_range"}),
            ),
        )
    )

    class StubResult:
        """Minimal analyze_metric_series result."""

        def __init__(self, points: tuple[MetricPoint, ...]) -> None:
            self.points = points

    points_by_key = {
        "damage_a": (
            MetricPoint(run_id=1, battle_date=datetime(2025, 12, 10, 1, 0, tzinfo=UTC), tier=None, preset_name=None, value=30.0),
            MetricPoint(run_id=2, battle_date=datetime(2025, 12, 10, 1, 0, tzinfo=UTC), tier=None, preset_name=None, value=0.0),
        ),
        "damage_b": (
            MetricPoint(run_id=1, battle_date=datetime(2025, 12, 10, 1, 0, tzinfo=UTC), tier=None, preset_name=None, value=70.0),
            MetricPoint(run_id=2, battle_date=datetime(2025, 12, 10, 1, 0, tzinfo=UTC), tier=None, preset_name=None, value=100.0),
        ),
    }

    def stub_analyze_metric_series(_records, *, metric_key: str, **_kwargs):  # type: ignore[no-untyped-def]
        return StubResult(points_by_key[metric_key])

    monkeypatch.setattr("core.charting.render.analyze_metric_series", stub_analyze_metric_series)

    config = ChartConfig(
        id="stacked",
        title="% Damage (Stacked)",
        description=None,
        category="damage",
        domain="damage",
        semantic_type="contribution",
        chart_type="bar",
        stacked=True,
        default_granularity="per_run",
        metric_series=(
            ChartSeriesConfig(metric_key="damage_a"),
            ChartSeriesConfig(metric_key="damage_b"),
        ),
        filters=ChartFilters(date_range=DateRangeFilterConfig(enabled=True, default_start=datetime(2025, 12, 9, tzinfo=UTC))),
        ui=ChartUI(show_by_default=False, selectable=True, order=0),
    )

    rendered = render_chart(
        config=config,
        records=[object()],
        registry=registry,
        granularity="per_run",
        moving_average_window=None,
        entity_selections={},
    )

    datasets = rendered.data["datasets"]
    assert len(datasets) == 2
    for idx in range(len(rendered.data["labels"])):
        values: list[float] = []
        for dataset in datasets:
            value = dataset["data"][idx]
            if value is None:
                continue
            values.append(float(value))
        total = sum(values)
        assert total == pytest.approx(100.0)
