"""Unit tests for Explore avg aggregation."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from analysis.explore_engine import execute_explore_query
from analysis.explore_registry import DEFAULT_BREAKDOWNS, build_explore_metric_registry
from analysis.explore_schema import ExploreBreakdown, ExploreMetricSelection, ExploreQuery, ExploreScope

pytestmark = pytest.mark.unit


@dataclass
class DummyRun:
    """Minimal run container for Explore aggregation tests."""

    id: int
    tier: int
    coins_earned: int
    real_time_seconds: int


def test_execute_explore_query_avg_aggregation() -> None:
    """Avg aggregation computes per-group means."""

    records = [
        DummyRun(id=1, tier=7, coins_earned=3600, real_time_seconds=3600),
        DummyRun(id=2, tier=7, coins_earned=7200, real_time_seconds=3600),
        DummyRun(id=3, tier=8, coins_earned=3600, real_time_seconds=1800),
    ]
    query = ExploreQuery(
        schema_version="1.0",
        player_id="player-1",
        name="Avg coins/hour by tier",
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
        metric=ExploreMetricSelection(key="coins_per_hour", aggregation="avg"),
        visualization_hint="table",
    )
    registry = build_explore_metric_registry()

    result = execute_explore_query(
        records,
        query=query,
        metric_registry=registry,
        breakdown_registry=DEFAULT_BREAKDOWNS,
    )

    assert len(result.rows) == 2
    assert result.rows[0].breakdown == ("Tier 7",)
    assert result.rows[0].sample_count == 2
    assert result.rows[0].value == pytest.approx(5400.0)
    assert result.rows[1].breakdown == ("Tier 8",)
    assert result.rows[1].sample_count == 1
    assert result.rows[1].value == pytest.approx(7200.0)
