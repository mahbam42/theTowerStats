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
    game_time_seconds: int | None = None


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
        name="Avg coins by tier",
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
        metrics=(ExploreMetricSelection(key="coins_earned", aggregation="avg"),),
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
    assert result.rows[0].sample_count == 2
    assert result.rows[0].value == pytest.approx(5400.0)
    assert result.rows[1].breakdown == ("Tier 8",)
    assert result.rows[1].sample_count == 1
    assert result.rows[1].value == pytest.approx(3600.0)


def test_execute_explore_query_real_and_game_time_hour_breakdowns() -> None:
    """Bucket runs by real-time and game-time hour durations."""

    records = [
        DummyRun(id=1, tier=7, coins_earned=100, real_time_seconds=3500, game_time_seconds=4000),
        DummyRun(id=2, tier=7, coins_earned=200, real_time_seconds=7200, game_time_seconds=8000),
    ]
    registry = build_explore_metric_registry()

    real_time_query = ExploreQuery(
        schema_version="1.0",
        player_id="player-1",
        name="Coins by real-time hour",
        scope=ExploreScope(
            start_date=None,
            end_date=None,
            tier=None,
            preset_id=None,
            snapshot_id=None,
            past_n_runs=None,
        ),
        filters=(),
        breakdowns=(ExploreBreakdown(dimension="real_time_hour", order=1),),
        metrics=(ExploreMetricSelection(key="coins_earned", aggregation="sum"),),
        visualization_hint="table",
    )
    real_time_result = execute_explore_query(
        records,
        query=real_time_query,
        metric_selection=real_time_query.metrics[0],
        metric_registry=registry,
        breakdown_registry=DEFAULT_BREAKDOWNS,
    )

    assert {row.breakdown for row in real_time_result.rows} == {
        ("Real Time Hour 1",),
        ("Real Time Hour 3",),
    }

    game_time_query = ExploreQuery(
        schema_version="1.0",
        player_id="player-1",
        name="Coins by game-time hour",
        scope=ExploreScope(
            start_date=None,
            end_date=None,
            tier=None,
            preset_id=None,
            snapshot_id=None,
            past_n_runs=None,
        ),
        filters=(),
        breakdowns=(ExploreBreakdown(dimension="game_time_hour", order=1),),
        metrics=(ExploreMetricSelection(key="coins_earned", aggregation="sum"),),
        visualization_hint="table",
    )
    game_time_result = execute_explore_query(
        records,
        query=game_time_query,
        metric_selection=game_time_query.metrics[0],
        metric_registry=registry,
        breakdown_registry=DEFAULT_BREAKDOWNS,
    )

    assert {row.breakdown for row in game_time_result.rows} == {
        ("Game Time Hour 2",),
        ("Game Time Hour 3",),
    }
