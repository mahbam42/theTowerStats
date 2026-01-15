"""Unit tests for Explore percent-of-total output."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from analysis.explore_engine import execute_explore_query
from analysis.explore_registry import DEFAULT_BREAKDOWNS, build_explore_metric_registry
from analysis.explore_schema import ExploreBreakdown, ExploreMetricSelection, ExploreQuery, ExploreScope

pytestmark = pytest.mark.unit


@dataclass
class DummyRun:
    """Minimal run container for Explore percent-of-total tests."""

    id: int
    tier: int
    coins_earned: int


def test_execute_explore_query_percent_of_total_sum() -> None:
    """Percent-of-total uses summed metric values per breakdown."""

    records = [
        DummyRun(id=1, tier=7, coins_earned=20),
        DummyRun(id=2, tier=7, coins_earned=30),
        DummyRun(id=3, tier=8, coins_earned=50),
    ]
    query = ExploreQuery(
        schema_version="1.0",
        player_id="player-1",
        name="Coins share by tier",
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
                aggregation="sum",
                percent_of_total=True,
            ),
        ),
        visualization_hint="table",
    )
    registry = build_explore_metric_registry()

    result = execute_explore_query(
        records,
        query=query,
        metric_selection=query.metrics[0],
        metric_registry=registry,
        breakdown_registry=DEFAULT_BREAKDOWNS,
    )

    assert len(result.rows) == 2
    assert result.rows[0].breakdown == ("Tier 7",)
    assert result.rows[0].value == pytest.approx(50.0)
    assert result.rows[1].breakdown == ("Tier 8",)
    assert result.rows[1].value == pytest.approx(50.0)
    assert result.total_value == pytest.approx(100.0)


def test_execute_explore_query_percent_of_total_zero_total() -> None:
    """Percent-of-total yields blank values when totals are zero."""

    records = [
        DummyRun(id=1, tier=7, coins_earned=0),
        DummyRun(id=2, tier=8, coins_earned=0),
    ]
    query = ExploreQuery(
        schema_version="1.0",
        player_id="player-1",
        name="Zero coins",
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
                aggregation="sum",
                percent_of_total=True,
            ),
        ),
        visualization_hint="table",
    )
    registry = build_explore_metric_registry()

    result = execute_explore_query(
        records,
        query=query,
        metric_selection=query.metrics[0],
        metric_registry=registry,
        breakdown_registry=DEFAULT_BREAKDOWNS,
    )

    assert all(row.value is None for row in result.rows)
    assert result.total_value is None
