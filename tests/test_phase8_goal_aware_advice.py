"""Phase 8 Pillar 2 goal-aware advice tests."""

from __future__ import annotations

import pytest

from core.advice import GoalScopeSample, GoalWeights, INSUFFICIENT_DATA_MESSAGE, generate_goal_weighted_advice

pytestmark = pytest.mark.unit


def test_goal_weighted_advice_degrades_with_thin_scopes() -> None:
    """Goal-aware advice degrades deterministically when either scope is too thin."""

    items = generate_goal_weighted_advice(
        goal_label="Hybrid",
        baseline=GoalScopeSample(
            label="Snapshot A",
            runs_coins_per_hour=2,
            runs_coins_per_wave=3,
            runs_waves_reached=3,
            coins_per_hour=100.0,
            coins_per_wave=10.0,
            waves_reached=100.0,
        ),
        comparison=GoalScopeSample(
            label="Current filters",
            runs_coins_per_hour=3,
            runs_coins_per_wave=3,
            runs_waves_reached=3,
            coins_per_hour=110.0,
            coins_per_wave=11.0,
            waves_reached=105.0,
        ),
        weights=GoalWeights(coins_per_hour=1.0, coins_per_wave=0.5, waves_reached=0.75),
    )
    assert items
    assert INSUFFICIENT_DATA_MESSAGE in items[0].title


def test_goal_weighted_advice_computes_transparent_score() -> None:
    """Goal-aware advice computes a weighted percent index with an explicit formula."""

    items = generate_goal_weighted_advice(
        goal_label="Economy / Farming",
        baseline=GoalScopeSample(
            label="Snapshot A",
            runs_coins_per_hour=3,
            runs_coins_per_wave=3,
            runs_waves_reached=3,
            coins_per_hour=100.0,
            coins_per_wave=10.0,
            waves_reached=100.0,
        ),
        comparison=GoalScopeSample(
            label="Snapshot B",
            runs_coins_per_hour=3,
            runs_coins_per_wave=3,
            runs_waves_reached=3,
            coins_per_hour=110.0,
            coins_per_wave=11.0,
            waves_reached=90.0,
        ),
        weights=GoalWeights(coins_per_hour=1.0, coins_per_wave=1.0, waves_reached=0.0),
    )
    assert items
    assert "For your selected goal: Economy / Farming" in items[0].title
    assert "score = (" in items[0].context
