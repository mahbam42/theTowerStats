"""Unit tests for goal cost breakdown computations."""

from __future__ import annotations

import pytest

from analysis.goals import compute_goal_cost_breakdown

pytestmark = pytest.mark.unit


def test_compute_goal_cost_breakdown_sums_per_level_costs() -> None:
    """Totals include each upgrade step from current to target."""

    breakdown = compute_goal_cost_breakdown(
        costs_by_level={1: "5", 2: "7", 3: "9"},
        currency="medals",
        current_level_display=1,
        current_level_for_calc=0,
        current_is_assumed=True,
        target_level=3,
    )
    assert breakdown.total_remaining == 21
    assert breakdown.total_to_target == 21
    assert breakdown.total_invested == 0
    assert [(step.from_level, step.to_level, step.cost_amount) for step in breakdown.per_level] == [
        (0, 1, 5),
        (1, 2, 7),
        (2, 3, 9),
    ]
    assert any("computed from 0" in note for note in breakdown.assumptions)


def test_compute_goal_cost_breakdown_is_zero_when_target_reached() -> None:
    """No remaining cost is reported when target is at or below current."""

    breakdown = compute_goal_cost_breakdown(
        costs_by_level={1: "5"},
        currency="stones",
        current_level_display=2,
        current_level_for_calc=2,
        current_is_assumed=False,
        target_level=2,
    )
    assert breakdown.total_remaining == 0
    assert breakdown.per_level == ()
