"""Unit tests for Explore schema validation rules."""

from __future__ import annotations

import pytest

from analysis.explore_registry import build_explore_metric_registry
from analysis.explore_schema import (
    ExploreBreakdown,
    ExploreMetricSelection,
    ExploreQuery,
    ExploreScope,
    validate_explore_query,
)

pytestmark = pytest.mark.unit


def test_validate_explore_query_requires_breakdown_for_percent_of_total() -> None:
    """Percent-of-total requires at least one breakdown."""

    registry = build_explore_metric_registry()
    query = ExploreQuery(
        schema_version="1.0",
        player_id="player-1",
        name="Coins share",
        scope=ExploreScope(
            start_date=None,
            end_date=None,
            tier=None,
            preset_id=None,
            snapshot_id=None,
            past_n_runs=None,
        ),
        filters=(),
        breakdowns=(),
        metrics=(
            ExploreMetricSelection(
                key="coins_earned",
                aggregation="sum",
                percent_of_total=True,
            ),
        ),
        visualization_hint="table",
    )

    result = validate_explore_query(query, metric_registry=registry)

    assert any("Percent-of-total" in error for error in result.errors)


def test_validate_explore_query_rejects_percent_of_total_avg() -> None:
    """Percent-of-total cannot be used with averages."""

    registry = build_explore_metric_registry()
    query = ExploreQuery(
        schema_version="1.0",
        player_id="player-1",
        name="Avg percent",
        scope=ExploreScope(
            start_date=None,
            end_date=None,
            tier=None,
            preset_id=None,
            snapshot_id=None,
            past_n_runs=None,
        ),
        filters=(),
        breakdowns=(ExploreBreakdown(dimension="tier", order=1),),
        metrics=(
            ExploreMetricSelection(
                key="coins_earned",
                aggregation="avg",
                percent_of_total=True,
            ),
        ),
        visualization_hint="table",
    )

    result = validate_explore_query(query, metric_registry=registry)

    assert any("Percent-of-total requires sum or count" in error for error in result.errors)


def test_validate_explore_query_accepts_resource_rate_metrics() -> None:
    """Per-hour resource metrics validate against the registry."""

    registry = build_explore_metric_registry()
    query = ExploreQuery(
        schema_version="1.0",
        player_id="player-1",
        name="Resource rates",
        scope=ExploreScope(
            start_date=None,
            end_date=None,
            tier=None,
            preset_id=None,
            snapshot_id=None,
            past_n_runs=None,
        ),
        filters=(),
        breakdowns=(ExploreBreakdown(dimension="tier", order=1),),
        metrics=(
            ExploreMetricSelection(key="cells_per_hour", aggregation="avg"),
            ExploreMetricSelection(key="reroll_shards_per_hour", aggregation="avg"),
        ),
        visualization_hint="table",
    )

    result = validate_explore_query(query, metric_registry=registry)

    assert result.errors == ()
