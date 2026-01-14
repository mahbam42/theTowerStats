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
    assert result.query.metric.key == "recovery_packages"
    assert result.query.metric.aggregation == "sum"
