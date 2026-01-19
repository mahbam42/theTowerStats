"""Unit tests for the Explore DSL parser."""

from __future__ import annotations

from datetime import date

import pytest

from analysis.explore_dsl import parse_explore_dsl
from analysis.explore_schema import ExploreScope

pytestmark = pytest.mark.unit


def test_parse_explore_dsl_with_placeholders_uses_defaults() -> None:
    """Parse DSL and apply default scope values to placeholders."""

    default_scope = ExploreScope(
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 10),
        tier=7,
        preset_id=12,
        snapshot_id=None,
        past_n_runs=30,
    )
    dsl_text = (
        'name "Tier 7 breakdown"\n'
        "scope date [date:YYYY-MM-DD]..[date:YYYY-MM-DD] not 2025-01-05, 2025-01-07\n"
        "scope tier >8 not tournament\n"
        "scope preset farm, event push not speed run\n"
        "scope snapshot [snapshot:—]\n"
        "scope past_n_runs [runs:—]\n"
        "filter wave 100..200\n"
        "breakdown by tier then run\n"
        "metric recovery_packages sum\n"
        "output table\n"
    )

    result = parse_explore_dsl(dsl_text, player_id="player-1", default_scope=default_scope)

    assert result.errors == ()
    assert result.query is not None
    assert result.query.scope.tier == 7
    assert any(
        entry.field == "tournament" and entry.operator == "=" and entry.value is False
        for entry in result.query.filters
    )
    assert any(
        entry.field == "tier" and entry.operator == ">=" and entry.value == 9
        for entry in result.query.filters
    )
    assert any(
        entry.field == "date_exclude" and entry.operator == "in" and entry.value == ["2025-01-05", "2025-01-07"]
        for entry in result.query.filters
    )
    assert any(
        entry.field == "preset_name_include"
        and entry.operator == "in"
        and entry.value == ["farm", "event push"]
        for entry in result.query.filters
    )
    assert any(
        entry.field == "preset_name_exclude"
        and entry.operator == "in"
        and entry.value == ["speed run"]
        for entry in result.query.filters
    )
    assert result.query.scope.start_date == date(2025, 1, 1)
    assert result.query.scope.end_date == date(2025, 1, 10)
    assert result.query.scope.preset_id == 12
    assert result.query.scope.past_n_runs == 30
    assert result.query.breakdowns[0].dimension == "tier"
    assert result.query.breakdowns[1].dimension == "run"
    assert result.query.metrics[0].key == "recovery_packages"
    assert result.query.metrics[0].aggregation == "sum"


def test_parse_explore_dsl_all_tokens_clear_defaults() -> None:
    """Parse DSL and allow all/* to clear prefilled scope values."""

    default_scope = ExploreScope(
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 10),
        tier=7,
        preset_id=12,
        snapshot_id=3,
        past_n_runs=30,
    )
    dsl_text = (
        'name "All scope"\n'
        "scope date all not 2025-01-05\n"
        "scope tier *\n"
        "scope preset all\n"
        "scope snapshot *\n"
        "scope past_n_runs all\n"
        "metric coins_earned sum\n"
    )

    result = parse_explore_dsl(dsl_text, player_id="player-1", default_scope=default_scope)

    assert result.errors == ()
    assert result.query is not None
    assert result.query.scope.start_date is None
    assert result.query.scope.end_date is None
    assert result.query.scope.tier is None
    assert result.query.scope.preset_id is None
    assert result.query.scope.snapshot_id is None
    assert result.query.scope.past_n_runs is None
    assert any(
        entry.field == "date_exclude" and entry.operator == "in" and entry.value == ["2025-01-05"]
        for entry in result.query.filters
    )


def test_parse_explore_dsl_defaults_metric_aggregation() -> None:
    """Metric lines without aggregation default to sum."""

    default_scope = ExploreScope(
        start_date=None,
        end_date=None,
        tier=None,
        preset_id=None,
        snapshot_id=None,
        past_n_runs=None,
    )
    dsl_text = 'name "Metric default"\nmetric coins_earned\nbreakdown by run\n'

    result = parse_explore_dsl(dsl_text, player_id="player-1", default_scope=default_scope)

    assert result.errors == ()
    assert result.query is not None
    assert result.query.metrics[0].key == "coins_earned"
    assert result.query.metrics[0].aggregation == "sum"


def test_parse_explore_dsl_breakdown_accepts_and_separator() -> None:
    """Breakdown lines accept 'and' as a separator."""

    default_scope = ExploreScope(
        start_date=None,
        end_date=None,
        tier=None,
        preset_id=None,
        snapshot_id=None,
        past_n_runs=None,
    )
    dsl_text = 'name "Breakdown and"\nbreakdown by run and tier\nmetric coins_earned\n'

    result = parse_explore_dsl(dsl_text, player_id="player-1", default_scope=default_scope)

    assert result.errors == ()
    assert result.query is not None
    assert [entry.dimension for entry in result.query.breakdowns] == ["run", "tier"]


def test_parse_explore_dsl_supports_avg_aggregation() -> None:
    """Metric lines accept avg aggregation."""

    default_scope = ExploreScope(
        start_date=None,
        end_date=None,
        tier=None,
        preset_id=None,
        snapshot_id=None,
        past_n_runs=None,
    )
    dsl_text = 'name "Average coins per hour"\nmetric coins_per_hour avg\nbreakdown by tier\n'

    result = parse_explore_dsl(dsl_text, player_id="player-1", default_scope=default_scope)

    assert result.errors == ()
    assert result.query is not None
    assert result.query.metrics[0].key == "coins_per_hour"
    assert result.query.metrics[0].aggregation == "avg"


def test_parse_explore_dsl_supports_multiple_metrics() -> None:
    """Metric lines accept multiple metrics joined by and."""

    default_scope = ExploreScope(
        start_date=None,
        end_date=None,
        tier=None,
        preset_id=None,
        snapshot_id=None,
        past_n_runs=None,
    )
    dsl_text = (
        'name "Multi metrics"\n'
        "metric coins_per_hour avg and cells_earned avg\n"
        "breakdown by tier\n"
    )

    result = parse_explore_dsl(dsl_text, player_id="player-1", default_scope=default_scope)

    assert result.errors == ()
    assert result.query is not None
    assert [metric.key for metric in result.query.metrics] == ["coins_per_hour", "cells_earned"]
    assert [metric.aggregation for metric in result.query.metrics] == ["avg", "avg"]


@pytest.mark.golden
def test_parse_explore_dsl_supports_percent_of_total() -> None:
    """Metric lines accept the percent-of-total modifier."""

    default_scope = ExploreScope(
        start_date=None,
        end_date=None,
        tier=None,
        preset_id=None,
        snapshot_id=None,
        past_n_runs=None,
    )
    dsl_text = (
        'name "Coin share"\n'
        "metric coins_earned sum percent_of_total\n"
        "breakdown by tier\n"
    )

    result = parse_explore_dsl(dsl_text, player_id="player-1", default_scope=default_scope)

    assert result.errors == ()
    assert result.query is not None
    assert result.query.metrics[0].key == "coins_earned"
    assert result.query.metrics[0].aggregation == "sum"
    assert result.query.metrics[0].percent_of_total is True


@pytest.mark.regression
def test_parse_explore_dsl_rejects_multi_separator_date_ranges() -> None:
    """Reject date ranges that include multiple separators."""

    default_scope = ExploreScope(
        start_date=None,
        end_date=None,
        tier=None,
        preset_id=None,
        snapshot_id=None,
        past_n_runs=None,
    )
    dsl_text = (
        'name "Bad date range"\n'
        "scope date 2025-01-01..2025-01-05..2025-01-07\n"
        "metric coins_earned sum\n"
    )

    result = parse_explore_dsl(dsl_text, player_id="player-1", default_scope=default_scope)

    assert result.query is None
    assert "Date scope must use start..end format." in result.errors


@pytest.mark.unit
@pytest.mark.regression
def test_parse_explore_dsl_accepts_metric_aliases() -> None:
    """Normalize known metric aliases in the DSL."""

    default_scope = ExploreScope(
        start_date=None,
        end_date=None,
        tier=None,
        preset_id=None,
        snapshot_id=None,
        past_n_runs=None,
    )
    dsl_text = (
        'name "Alias check"\n'
        "metric enemies_destroyed_elites sum and run_duration avg\n"
        "breakdown by run\n"
    )

    result = parse_explore_dsl(dsl_text, player_id="player-1", default_scope=default_scope)

    assert result.errors == ()
    assert result.query is not None
    assert result.query.metrics[0].key == "enemies_destroyed_elite"
    assert result.query.metrics[1].key == "real_time_hours"
    assert any("enemies_destroyed_elites" in warning for warning in result.warnings)
    assert any("run_duration" in warning for warning in result.warnings)
